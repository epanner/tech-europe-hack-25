import json
from typing import Dict, Any, Optional
from backend.models import (
    CompanyInput,
    LawfulnessOfProcessing,
    DataSubjectRightsCompliance,
    RiskManagementAndSafeguards,
    AccountabilityAndGovernance,
)
from openai import OpenAI


class OpenAIGDPRReActAgent:
    """
    OpenAI-powered Reasoning and Acting (ReAct) Agent for collecting GDPR compliance information
    """
    
    def __init__(self, api_key: str = None, model: str = "gpt-4"):
        try:
            self.openai = OpenAI(api_key=api_key)
        except Exception:
            raise ValueError("OpenAI API key must be provided either as parameter or environment variable")
        
        self.model = model
        self.collected_data = {}
        self.conversation_history = []
        
        # Define the schema for OpenAI to understand
        self.schema_info = self._build_schema_info()
    
    def _build_schema_info(self) -> str:
        """
        Build comprehensive schema information for OpenAI
        """
        return """
        REQUIRED FIELDS TO COLLECT:
        
        1. data_type (str): Type of data involved in breach (e.g., "Health data", "PII", "Financial data")
        
        2. lawfulness_of_processing (enum): GDPR Article 6 legal basis assessment
           - "lawful and appropriate basis": Valid Article 6 basis with proper implementation
           - "lawful but principle violation": Has legal basis but violates GDPR principles
           - "no valid basis": No valid Article 6 legal basis
           - "exempt or restricted": Special exemptions apply
           - "information unavailable": User doesn't have the required information
        
        3. data_subject_rights_compliance (enum): GDPR Chapter III rights compliance
           - "full compliance": All data subject rights properly implemented
           - "partial compliance": Some rights implemented with gaps
           - "non compliance": Rights requests ignored or mishandled
           - "not triggered": No rights requests received
           - "information unavailable": User doesn't have the required information
        
        4. risk_management_and_safeguards (enum): GDPR Article 32 security measures
           - "proactive safeguards": Privacy by design, comprehensive security
           - "reactive only": Security measures only after incidents
           - "insufficient protection": Inadequate security for risk level
           - "not applicable": No personal data requiring safeguards
           - "information unavailable": User doesn't have the required information
        
        5. accountability_and_governance (enum): GDPR Article 5(2) governance framework
           - "fully accountable": DPO, DPIA, policies, documentation complete
           - "partially accountable": Some governance with gaps
           - "not accountable": No governance framework
           - "not required": Exempt from accountability requirements
           - "information unavailable": User doesn't have the required information
        """
    
    def analyze_user_input(self, user_input: str) -> Dict[str, Any]:
        """
        Use OpenAI to analyze user input and determine what information is present/missing
        """
        system_prompt = f"""
        You are an expert GDPR compliance analyst. Analyze the user's input to determine:
        1. What information is already provided
        2. What information is missing
        3. If the user was asked a question, make sure that extracted_data contains information only about this field
        
        {self.schema_info}
        
        CONVERSATION HISTORY: {json.dumps(self.conversation_history[-2:], indent=2)}

        CURRENT COLLECTED DATA: {json.dumps(self.collected_data, indent=2)}
        
        Respond with a JSON object containing:
        {{
            "extracted_data": {{
                "field_name": "extracted_value_or_enum_option",
                // Only include fields where you're confident about the extraction
                // Only include fields about which you asked the question
            }},
            "missing_fields": ["field1", "field2", ...],
            "confidence_scores": {{
                "field_name": 0.0-1.0,
                // Confidence in extracted data
            }},
            "analysis_reasoning": "Brief explanation of your analysis"
        }}
        
        For enum fields, make sure the extracted value exactly matches one of the enum options.
        """
        
        try:
            response = self.openai.responses.create(
                model=self.model,
                input=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"User input: {user_input}"}
                ],
                temperature=0.1
            )
            
            # Try to parse JSON response
            try:
                return json.loads(response.output_text)
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return {
                    "extracted_data": {},
                    "missing_fields": list(self._get_required_fields() - set(self.collected_data.keys())),
                    "confidence_scores": {},
                    "analysis_reasoning": "Failed to parse OpenAI response as JSON"
                }
                
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return {
                "extracted_data": {},
                "missing_fields": list(self._get_required_fields() - set(self.collected_data.keys())),
                "confidence_scores": {},
                "analysis_reasoning": f"API Error: {str(e)}"
            }
    
    def generate_question(self, missing_field: str) -> str:
        """
        Use OpenAI to generate contextual questions for missing fields
        """
        system_prompt = f"""
        You are an expert GDPR consultant helping collect compliance information. 
        Generate a clear, helpful question to gather the missing information for: {missing_field}
        
        {self.schema_info}
        
        CONTEXT:
        - Current conversation: {json.dumps(self.conversation_history, indent=2)}
        - Already collected: {json.dumps(self.collected_data, indent=2)}
        - Missing field: {missing_field}
        
        REQUIREMENTS:
        0. Don't ask questions about fields that user already answered
        1. Ask ONE clear, specific question
        2. Provide context about why this information is needed (GDPR perspective)
        3. Give examples or options when helpful
        4. Keep it conversational but professional
        
        Ask questions only about missing fields
        Generate ONLY the question text, no JSON or formatting.
        """
        
        try:
            response =self.openai.responses.create(
                model=self.model,
                input=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Generate a question for missing field: {missing_field}"}
                ],
                temperature=0.3
            )
            
            return response.output_text
            
        except Exception as e:
            print(f"Error generating question: {e}")
            return self._fallback_question(missing_field)
    
    def _fallback_question(self, field: str) -> str:
        """
        Fallback questions if OpenAI is unavailable
        """
        fallback_questions = {
            "data_type": "What type of personal data was involved in the breach? (e.g., Health data, PII, Financial records)",
            "lawfulness_of_processing": "What was the legal basis for processing this data under GDPR Article 6?",
            "data_subject_rights_compliance": "How well has your organization handled data subject rights requests?",
            "risk_management_and_safeguards": "What security measures did you have in place before the breach?",
            "accountability_and_governance": "What governance structures do you have for data protection compliance?"
        }
        return fallback_questions.get(field, f"Please provide information about: {field}")
    
    def _get_required_fields(self) -> set:
        """
        Get set of all required field names
        """
        return {
            "data_type", "lawfulness_of_processing",
            "data_subject_rights_compliance", "risk_management_and_safeguards",
            "accountability_and_governance"
        }
    
    def _validate_enum_value(self, field: str, value: str) -> bool:
        """
        Validate that enum values match exactly
        """
        enum_mappings = {
            "lawfulness_of_processing": [e.value for e in LawfulnessOfProcessing],
            "data_subject_rights_compliance": [e.value for e in DataSubjectRightsCompliance],
            "risk_management_and_safeguards": [e.value for e in RiskManagementAndSafeguards],
            "accountability_and_governance": [e.value for e in AccountabilityAndGovernance]
        }
        
        if field in enum_mappings:
            return value in enum_mappings[field]
        return True  # Non-enum fields
    
    async def process_user_input(self, user_input: str) -> str:
        """
        Main processing method implementing ReAct pattern with OpenAI
        """
        self.conversation_history.append({
            "role": "user",
            "content": user_input
        })
        
        # REASONING: Use OpenAI to analyze the input
        analysis = self.analyze_user_input(user_input)
        
        # Update collected data with validated extractions
        if analysis.get("extracted_data"):
            for field, value in analysis["extracted_data"].items():
                if self._validate_enum_value(field, value):
                    self.collected_data[field] = value
                    print(f"✓ Extracted {field}: {value}")
        
        # ACTING: Determine next action
        missing_fields = list(self._get_required_fields() - set(self.collected_data.keys()))
        
        if not missing_fields:
            # All data collected - create and validate the model
            try:
                company_input = CompanyInput(**self.collected_data)
                response = f"""Perfect! I have collected all the required GDPR compliance information:

📊 **DATA COLLECTION COMPLETE** 📊

{self._format_collected_data()}

Is this information accurate? If you need to modify anything, please let me know!

Analysis: {analysis.get('analysis_reasoning', 'Complete data set validated.')}"""
                
            except Exception as e:
                response = f"I have all fields but there's a validation error: {str(e)}. Please help me correct this."
        
        else:
            # Generate question for next missing field
            next_field = missing_fields[0]
            question = self.generate_question(next_field)
            
            response = f"""I understand: {analysis.get('analysis_reasoning', 'Analyzing your input...')}

**Next, I need information about: `{next_field.replace('_', ' ').title()}`**

{question}

Progress: {len(self.collected_data)}/{len(self._get_required_fields())} fields collected ✅"""
        
        self.conversation_history.append({
            "role": "assistant",
            "content": response
        })
        
        return response
    
    def _format_collected_data(self) -> str:
        """
        Format collected data for display
        """
        formatted = ""
        field_labels = {
            "data_type": "📊 Data Type Breached",
            "lawfulness_of_processing": "⚖️ Lawfulness of Processing",
            "data_subject_rights_compliance": "👤 Data Subject Rights Compliance",
            "risk_management_and_safeguards": "🔒 Risk Management & Safeguards",
            "accountability_and_governance": "📋 Accountability & Governance"
        }
        
        for field, value in self.collected_data.items():
            label = field_labels.get(field, field.replace('_', ' ').title())
            formatted += f"{label}: {value}\n"
        
        return formatted
    
    def get_company_input_model(self) -> Optional[CompanyInput]:
        """
        Return the validated CompanyInput model if all data is collected
        """
        if len(self.collected_data) == len(self._get_required_fields()):
            try:
                return CompanyInput(**self.collected_data)
            except Exception as e:
                print(f"Model validation error: {e}")
                return None
        return None
    
    def reset(self):
        """
        Reset the agent state
        """
        self.collected_data = {}
        self.conversation_history = []
        print("🔄 Agent state reset. Ready to start fresh!")
    

# Synchronous wrapper for easier usage
class OpenAIGDPRReActAgentSync:
    """
    Synchronous wrapper for the async OpenAI agent
    """
    def __init__(self, api_key: str = None, model: str = "gpt-4"):
        import asyncio
        self.agent = OpenAIGDPRReActAgent(api_key, model)
        self.loop = asyncio.new_event_loop()
    
    def process_user_input(self, user_input: str) -> str:
        return self.loop.run_until_complete(self.agent.process_user_input(user_input))
    
    def reset(self):
        self.agent.reset()
    
    def get_company_input_model(self) -> Optional[CompanyInput]:
        return self.agent.get_company_input_model()
    
    @property
    def collected_data(self):
        return self.agent.collected_data

