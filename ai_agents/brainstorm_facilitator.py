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
    synergy_insights: Optional[List[str]] = None
    timestamp: datetime = datetime.now()
    session_id: str = datetime.now().strftime("%Y%m%d_%H%M%S")

class BrainstormFacilitator:
    def __init__(self, model: str = "gemini-2.0-flash", num_agents: int = 3):
        """Initialize the Brainstorm Facilitator with parallel ideation system."""
        self.model = model
        self.parallel_ideation = ParallelIdeationSystem(model, num_agents)
        
        # Configure Gemini for main facilitator
        api_key = os.getenv("VITE_GEMINI_API_KEY")
        if not api_key:
            raise ValueError("VITE_GEMINI_API_KEY not found in environment variables")
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
            
            # Run parallel ideation
            consolidated_ideas = await self.parallel_ideation.run_parallel_ideation(context)
            
            # Generate final recommendation and insights
            recommendation_prompt = f"""Review these consolidated solution ideas and provide a final recommendation:
            {json.dumps(consolidated_ideas, indent=2)}
            
            Product Context:
            {product_specs}
            
            Create a comprehensive recommendation that:
            1. Highlights the most promising solution(s)
            2. Explains key synergies between different specializations
            3. Addresses potential challenges and mitigation strategies
            
            Format as JSON with fields:
            - recommendation: string
            - synergy_insights: list of strings
            """
            
            response = await self.client.generate_content(recommendation_prompt)
            recommendation_data = json.loads(response.text)
            
            # Convert consolidated ideas to SolutionIdea objects
            solution_ideas = []
            for idea in consolidated_ideas:
                # Extract pros and cons from description
                pros_cons_prompt = f"""Analyze this solution idea and extract key pros and cons:
                Title: {idea['title']}
                Description: {idea['description']}
                Key Features: {', '.join(idea['key_features'])}
                Technical Approach: {', '.join(idea['technical_approach'])}
                
                Return as JSON with fields:
                - pros: list of strings
                - cons: list of strings
                """
                
                pros_cons_response = await self.client.generate_content(pros_cons_prompt)
                pros_cons_data = json.loads(pros_cons_response.text)
                
                solution_ideas.append(SolutionIdea(
                    title=idea["title"],
                    description=idea["description"],
                    key_features=idea["key_features"],
                    technical_approach=idea["technical_approach"],
                    pros=pros_cons_data["pros"],
                    cons=pros_cons_data["cons"],
                    score=idea.get("final_score", 0.0),
                    contributing_specializations=idea.get("contributing_specializations", []),
                    source_fragments=idea.get("source_fragments", []),
                    synergy_score=idea.get("synergy_score", 0.0)
                ))
            
            # Create and return final outcome
            return BrainstormOutcome(
                ideas=solution_ideas,
                consolidated_recommendation=recommendation_data["recommendation"],
                synergy_insights=recommendation_data["synergy_insights"],
                session_id=context.session_id
            )
            
        except Exception as e:
            logger.error(f"Error generating ideas: {str(e)}")
            raise
    
    def save_outcome(self, outcome: BrainstormOutcome, output_file: str):
        """Save the brainstorm outcome to a markdown file."""
        try:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            markdown_content = f"""# Brainstorm Session Outcome
Session ID: {outcome.session_id}
Timestamp: {outcome.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

## Consolidated Recommendation
{outcome.consolidated_recommendation}

## Synergy Insights
{chr(10).join(f'- {insight}' for insight in (outcome.synergy_insights or []))}

## Solution Ideas

"""
            # Add each solution idea
            for i, idea in enumerate(outcome.ideas, 1):
                markdown_content += f"""### {i}. {idea.title}
**Score: {idea.score:.2f}** | **Synergy Score: {idea.synergy_score or 0:.2f}**

{idea.description}

#### Key Features
{chr(10).join(f'- {feature}' for feature in idea.key_features)}

#### Technical Approach
{chr(10).join(f'- {step}' for step in idea.technical_approach)}

#### Pros
{chr(10).join(f'- {pro}' for pro in idea.pros)}

#### Cons
{chr(10).join(f'- {con}' for con in idea.cons)}

#### Contributing Specializations
{chr(10).join(f'- {spec}' for spec in (idea.contributing_specializations or []))}

---
"""
            
            # Write to file
            with output_path.open('w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            logger.info(f"Brainstorm outcome saved to {output_file}")
            
        except Exception as e:
            logger.error(f"Error saving outcome: {str(e)}")
            raise

@click.command()
@click.argument('specs_file', type=click.Path(exists=True))
@click.argument('output', type=click.Path())
@click.option('--num-agents', default=3, help='Number of parallel ideation agents')
@click.option('--market-context', type=str, help='Optional market context file')
@click.option('--constraints-file', type=click.Path(exists=True), help='Optional technical constraints file')
@click.option('--targets-file', type=click.Path(exists=True), help='Optional innovation targets file')
async def main(specs_file: str, 
               output: str, 
               num_agents: int,
               market_context: Optional[str] = None,
               constraints_file: Optional[str] = None,
               targets_file: Optional[str] = None):
    """Generate solution ideas using the Brainstorm Facilitator agent."""
    try:
        # Read input files
        with open(specs_file, 'r') as f:
            product_specs = f.read()
        
        technical_constraints = None
        if constraints_file:
            with open(constraints_file, 'r') as f:
                technical_constraints = f.read().splitlines()
        
        innovation_targets = None
        if targets_file:
            with open(targets_file, 'r') as f:
                innovation_targets = f.read().splitlines()
        
        # Initialize facilitator and generate ideas
        facilitator = BrainstormFacilitator(num_agents=num_agents)
        outcome = await facilitator.generate_ideas(
            product_specs=product_specs,
            market_context=market_context,
            technical_constraints=technical_constraints,
            innovation_targets=innovation_targets
        )
        
        # Save outcome
        facilitator.save_outcome(outcome, output)
        
    except Exception as e:
        logger.error(f"Error in brainstorm process: {str(e)}")
        raise

if __name__ == '__main__':
    asyncio.run(main())
