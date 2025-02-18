import click
from loguru import logger
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from pydantic import BaseModel
import json
import os
from dotenv import load_dotenv
import asyncio
from datetime import datetime
from pathlib import Path
from .parallel_ideation import ParallelIdeationSystem, IdeationContext

# Load environment variables
load_dotenv()

class SolutionIdea(BaseModel):
    title: str
    description: str
    key_features: List[str]
    technical_approach: List[str]
    pros: List[str]
    cons: List[str]
    score: float
    contributing_specializations: Optional[List[str]] = None
    source_fragments: Optional[List[str]] = None
    synergy_score: Optional[float] = None

class BrainstormOutcome(BaseModel):
    ideas: List[SolutionIdea]
    consolidated_recommendation: str
    timestamp: datetime = datetime.now()
    version: str = "3.2.0"

class BrainstormFacilitator:
    def __init__(self, model: str = "gemini-2.0-flash", num_agents: int = 3):
        """Initialize the Brainstorm Facilitator with parallel ideation system."""
        self.model = model
        self.parallel_ideation = ParallelIdeationSystem(model, num_agents)
        
        # Configure Gemini for main facilitator
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        genai.configure(api_key=api_key)
        self.client = genai.GenerativeModel(self.model)
    
    async def generate_ideas(self, 
                           product_specs: str, 
                           market_context: Optional[str] = None,
                           technical_constraints: Optional[List[str]] = None,
                           innovation_targets: Optional[List[str]] = None) -> BrainstormOutcome:
        """Generate multiple solution ideas using parallel ideation."""
        try:
            # Create ideation context
            context = IdeationContext(
                product_specs=product_specs,
                market_context=market_context,
                technical_constraints=technical_constraints,
                innovation_targets=innovation_targets
            )
            
            # Generate ideas in parallel
            ideas = await self.parallel_ideation.generate_ideas(context)
            
            # Consolidate recommendations
            consolidation_prompt = f"""
            You are a strategic innovation consultant tasked with consolidating multiple solution ideas into a final recommendation.
            Review the following solution ideas and provide a consolidated recommendation that captures the best aspects of each:

            {json.dumps([idea.dict() for idea in ideas], indent=2)}
            
            Focus on:
            1. Key synergies between ideas
            2. Most promising technical approaches
            3. Highest-value features
            4. Risk mitigation strategies
            
            Provide a clear, actionable recommendation in 2-3 paragraphs.
            """
            
            response = self.client.generate_content(consolidation_prompt)
            consolidated_recommendation = response.text
            
            # Create final outcome
            outcome = BrainstormOutcome(
                ideas=ideas,
                consolidated_recommendation=consolidated_recommendation
            )
            
            return outcome
            
        except Exception as e:
            logger.error(f"Error generating ideas: {str(e)}")
            raise
    
    def save_outcome(self, outcome: BrainstormOutcome, output_file: str) -> None:
        """Save the brainstorm outcome to a markdown file."""
        try:
            # Create output directory if it doesn't exist
            output_dir = os.path.dirname(output_file)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            
            # Format output as markdown
            markdown = f"""# Brainstorm Outcome
Version: {outcome.version}
Generated: {outcome.timestamp.isoformat()}

## Consolidated Recommendation
{outcome.consolidated_recommendation}

## Solution Ideas

"""
            # Add each idea
            for i, idea in enumerate(outcome.ideas, 1):
                markdown += f"""### {i}. {idea.title}
{idea.description}

**Key Features:**
{chr(10).join([f"- {feature}" for feature in idea.key_features])}

**Technical Approach:**
{chr(10).join([f"- {approach}" for approach in idea.technical_approach])}

**Pros:**
{chr(10).join([f"- {pro}" for pro in idea.pros])}

**Cons:**
{chr(10).join([f"- {con}" for con in idea.cons])}

Score: {idea.score}
"""
                if idea.contributing_specializations:
                    markdown += f"\nContributing Specializations: {', '.join(idea.contributing_specializations)}"
                if idea.synergy_score:
                    markdown += f"\nSynergy Score: {idea.synergy_score}"
                markdown += "\n\n"
            
            # Save to file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(markdown)
                
            logger.info(f"Saved brainstorm outcome to {output_file}")
            
        except Exception as e:
            logger.error(f"Error saving outcome: {str(e)}")
            raise

@click.group()
def cli():
    """Brainstorm Facilitator CLI"""
    pass

@cli.command()
def generate():
    """Generate brainstorm ideas and save outcome."""
    try:
        # Create artifacts directory
        artifacts_dir = Path("artifacts")
        artifacts_dir.mkdir(exist_ok=True)
        
        # Initialize facilitator
        facilitator = BrainstormFacilitator()
        
        # Read product specs if available
        specs_file = artifacts_dir / "PRODUCT_SPECS.md"
        product_specs = specs_file.read_text() if specs_file.exists() else "No product specs available"
        
        # Generate ideas
        outcome = asyncio.run(facilitator.generate_ideas(product_specs))
        
        # Save outcome
        output_file = artifacts_dir / "BRAINSTORM_OUTCOME.md"
        facilitator.save_outcome(outcome, str(output_file))
        
        logger.info("Successfully generated brainstorm outcome")
        
    except Exception as e:
        logger.error(f"Error in generate command: {str(e)}")
        raise

if __name__ == '__main__':
    cli()
