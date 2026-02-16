import json
from typing import Dict, List, Optional
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from ..core.config import settings

class ChangeAnalyzer:
    """AI-powered change significance analyzer"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0,
            api_key=settings.OPENAI_API_KEY
        )
    
    async def analyze_significance(self, 
                                   company_name: str,
                                   old_content: str,
                                   new_content: str,
                                   detected_changes: List[Dict]) -> Dict:
        """
        Analyze the business significance of detected changes
        """
        
        # Prepare change summary for the LLM
        change_summary = self._summarize_changes(detected_changes)
        
        system_prompt = """You are a business intelligence analyst specializing in competitive analysis.
        Your task is to analyze website changes and determine their strategic business significance.
        
        Rate significance from 0-100 based on these criteria:
        - Pricing changes: 80-100 (direct impact on revenue/competition)
        - New product launches: 70-90 (market expansion)
        - Key personnel changes: 60-80 (leadership/strategic direction)
        - Messaging/branding shifts: 40-70 (market positioning)
        - Feature updates: 30-60 (product evolution)
        - Minor copy edits: 0-30 (no strategic impact)
        - Legal/disclaimers: 10-40 (compliance, rarely strategic)
        
        Provide your analysis in JSON format with these fields:
        - score: integer 0-100
        - category: one of [pricing, product, messaging, team, legal, other]
        - justification: brief explanation
        - recommended_action: what a competitor should do
        - summary: one-line summary of the change
        """
        
        human_prompt = f"""
        Company: {company_name}
        
        Old content summary:
        {old_content[:1000]}...
        
        New content summary:
        {new_content[:1000]}...
        
        Detected changes:
        {change_summary}
        
        Analyze the strategic significance of these changes.
        """
        
        try:
            response = await self.llm.agenerate([
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ])
            
            # Parse JSON from response
            result_text = response.generations[0][0].text
            # Extract JSON if it's wrapped in markdown
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0]
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0]
            
            analysis = json.loads(result_text.strip())
            return analysis
            
        except Exception as e:
            print(f"❌ LLM analysis failed: {e}")
            # Fallback to rule-based analysis
            return self._rule_based_fallback(change_summary)
    
    def _summarize_changes(self, changes: List[Dict]) -> str:
        """Create a readable summary of changes for the LLM"""
        summary_lines = []
        for i, change in enumerate(changes[:5]):  # Limit to 5 changes
            change_type = change['type']
            old = change.get('old_section', '').strip()
            new = change.get('new_section', '').strip()
            
            if change_type == 'replace' and old and new:
                summary_lines.append(f"Replaced '{old[:100]}' with '{new[:100]}'")
            elif change_type == 'delete' and old:
                summary_lines.append(f"Removed: '{old[:100]}'")
            elif change_type == 'insert' and new:
                summary_lines.append(f"Added: '{new[:100]}'")
        
        return "\n".join(summary_lines) if summary_lines else "Minor text changes detected"
    
    def _rule_based_fallback(self, change_summary: str) -> Dict:
        """Fallback analyzer when LLM is unavailable"""
        # Simple keyword-based scoring
        keywords = {
            'price': 85, 'pricing': 85, 'cost': 80, 'discount': 80,
            'launch': 75, 'new': 60, 'product': 70, 'feature': 50,
            'ceo': 80, 'founder': 75, 'executive': 70, 'leadership': 70,
            'mission': 45, 'vision': 45, 'brand': 40, 'values': 40
        }
        
        score = 30  # Default medium-low significance
        category = 'other'
        
        change_lower = change_summary.lower()
        for word, word_score in keywords.items():
            if word in change_lower:
                if word_score > score:
                    score = word_score
                    if word in ['price', 'pricing', 'cost', 'discount']:
                        category = 'pricing'
                    elif word in ['launch', 'new', 'product', 'feature']:
                        category = 'product'
                    elif word in ['ceo', 'founder', 'executive', 'leadership']:
                        category = 'team'
                    elif word in ['mission', 'vision', 'brand', 'values']:
                        category = 'messaging'
        
        return {
            'score': score,
            'category': category,
            'justification': f"Rule-based analysis: detected keywords {[k for k in keywords if k in change_lower]}",
            'recommended_action': 'Monitor competitor closely',
            'summary': 'Website changes detected'
        }