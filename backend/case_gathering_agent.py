import openai
from pydantic import BaseModel
from typing import List, Dict, Any, AsyncGenerator, Optional
import json
import asyncio
import os


class BreachInfo(BaseModel):
    """Data structure to hold breach information as it's gathered"""
    case_description: str = ""
    lawfulness_of_processing: str = ""
    data_subject_rights_compliance: str = ""
    risk_management_and_safeguards: str = ""
    accountability_and_governance: str = ""
    conversation_complete: bool = False
    iteration_count: int = 0


class CaseGatheringAgent:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = openai.AsyncOpenAI(api_key=api_key)
        
        self.system_instructions = """You are an expert GDPR case analysis assistant helping Data Protection Officers classify breach incidents.

Your goal is to gather information through natural conversation to classify a GDPR breach case across 4 key dimensions:

1. **Lawfulness of Processing** (choose one):
   - lawful_and_appropriate_basis: Processing had clear legal basis and was appropriate
   - lawful_but_principle_violation: Legal basis existed but violated GDPR principles (fairness, transparency, etc.)
   - no_valid_basis: No valid legal basis for processing
   - exempt_or_restricted: Processing was exempt from GDPR or had restricted applicability

2. **Data Subject Rights Compliance** (choose one):
   - full_compliance: All relevant data subject rights were properly handled
   - partial_compliance: Some rights were handled but with deficiencies
   - non_compliance: Failed to respect data subject rights
   - not_triggered: No data subject rights were triggered in this case

3. **Risk Management and Safeguards** (choose one):
   - proactive_safeguards: Had comprehensive preventive security measures
   - reactive_only: Only responded after incident occurred
   - insufficient_protection: Inadequate security measures in place
   - not_applicable: Risk management not relevant to this case

4. **Accountability and Governance** (choose one):
   - fully_accountable: Complete documentation, policies, and governance
   - partially_accountable: Some accountability measures but gaps exist  
   - not_accountable: Failed to demonstrate compliance accountability
   - not_required: Accountability requirements didn't apply

**Your approach:**
- Ask focused, relevant questions to understand the case
- Be conversational and helpful, not interrogational
- Ask 1-2 questions at a time, don't overwhelm
- **CRITICAL: You have a maximum of 4 question rounds. After 4 exchanges, you MUST call finalize_classification even if information is incomplete**
- When you have enough information for all 4 dimensions OR after 4 exchanges, call the finalize_classification function immediately
- DO NOT ask for user confirmation of the classification - make the expert decision based on the information provided
- If the user provides a case description upfront, acknowledge it and ask follow-up questions for missing information
- Make reasonable inferences and expert judgments when information is incomplete

**Important:**
- Don't assume company size, revenue, or industry - focus on the incident itself
- Keep questions practical and specific to the breach incident
- Be empathetic - this person is dealing with a stressful situation
- Make classification decisions based on your expert knowledge even with incomplete information
- Once you have sufficient information OR reach 4 exchanges, classify immediately using the finalize_classification function
- If information is missing after 4 rounds, make reasonable inferences based on typical scenarios

**Examples of good questions:**
- "What type of personal data was involved in this incident?"
- "How did the breach occur? Was it due to a technical failure, human error, or malicious attack?"
- "What legal basis was your organization using to process this data?"
- "Were data subjects notified about the breach? If so, how and when?"
- "What security measures were in place before the incident occurred?"
- "How did your organization respond when the breach was discovered?"
- "Does your organization have documented data protection policies and procedures?"
"""
        
        self.current_breach_info = BreachInfo()
        
        # Define tools for function calling
        self.tools = [{
            "type": "function",
            "function": {
                "name": "finalize_classification",
                "description": "Finalize the breach classification with the gathered information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "case_description": {
                            "type": "string",
                            "description": "Complete description of the breach case"
                        },
                        "lawfulness_of_processing": {
                            "type": "string",
                            "enum": ["lawful_and_appropriate_basis", "lawful_but_principle_violation", "no_valid_basis", "exempt_or_restricted"],
                            "description": "Classification for lawfulness of processing"
                        },
                        "data_subject_rights_compliance": {
                            "type": "string", 
                            "enum": ["full_compliance", "partial_compliance", "non_compliance", "not_triggered"],
                            "description": "Classification for data subject rights compliance"
                        },
                        "risk_management_and_safeguards": {
                            "type": "string",
                            "enum": ["proactive_safeguards", "reactive_only", "insufficient_protection", "not_applicable"],
                            "description": "Classification for risk management and safeguards"
                        },
                        "accountability_and_governance": {
                            "type": "string",
                            "enum": ["fully_accountable", "partially_accountable", "not_accountable", "not_required"],
                            "description": "Classification for accountability and governance"
                        }
                    },
                    "required": ["case_description", "lawfulness_of_processing", "data_subject_rights_compliance", "risk_management_and_safeguards", "accountability_and_governance"]
                }
            }
        }]
    
    def finalize_classification(self, 
                              case_description: str,
                              lawfulness_of_processing: str, 
                              data_subject_rights_compliance: str,
                              risk_management_and_safeguards: str,
                              accountability_and_governance: str) -> str:
        """Finalize the breach classification with the gathered information"""
        
        # Validate the classification values
        valid_lawfulness = ["lawful_and_appropriate_basis", "lawful_but_principle_violation", "no_valid_basis", "exempt_or_restricted"]
        valid_rights = ["full_compliance", "partial_compliance", "non_compliance", "not_triggered"]
        valid_risk = ["proactive_safeguards", "reactive_only", "insufficient_protection", "not_applicable"]
        valid_governance = ["fully_accountable", "partially_accountable", "not_accountable", "not_required"]
        
        if (lawfulness_of_processing in valid_lawfulness and
            data_subject_rights_compliance in valid_rights and
            risk_management_and_safeguards in valid_risk and
            accountability_and_governance in valid_governance):
            
            self.current_breach_info = BreachInfo(
                case_description=case_description,
                lawfulness_of_processing=lawfulness_of_processing,
                data_subject_rights_compliance=data_subject_rights_compliance,
                risk_management_and_safeguards=risk_management_and_safeguards,
                accountability_and_governance=accountability_and_governance,
                conversation_complete=True
            )
            
            return f"""Perfect! I've classified your case as follows:

**Case Description:** {case_description}

**Classification:**
- **Lawfulness of Processing:** {lawfulness_of_processing}
- **Data Subject Rights Compliance:** {data_subject_rights_compliance}  
- **Risk Management and Safeguards:** {risk_management_and_safeguards}
- **Accountability and Governance:** {accountability_and_governance}

This classification will help with subsequent analysis and fine prediction. The case gathering is now complete."""
        else:
            return "I need to gather more information. Please provide additional details about the incident so I can properly classify it."

    async def start_conversation(self, initial_description: str = "") -> AsyncGenerator[str, None]:
        """Start a new case gathering conversation"""
        self.current_breach_info = BreachInfo()
        
        if initial_description:
            message = f"I need help classifying a GDPR breach case. Here's what I know so far: {initial_description}"
        else:
            message = "I need help classifying a GDPR breach case. I'd like to provide information about the incident."
        
        messages = [
            {"role": "system", "content": self.system_instructions},
            {"role": "user", "content": message}
        ]
        
        try:
            stream = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                tools=self.tools,
                stream=True,
                temperature=0.3
            )

            response_text = ""
            tool_call_id = None
            tool_call_args = ""
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    response_text += content
                    yield json.dumps({"type": "message", "data": content})
                
                # Handle tool calls - they might come in multiple chunks
                if chunk.choices[0].delta.tool_calls:
                    for tool_call in chunk.choices[0].delta.tool_calls:
                        if tool_call.function:
                            if tool_call.function.name == "finalize_classification":
                                tool_call_id = tool_call.id
                                # Arguments might come in chunks, so accumulate them
                                if tool_call.function.arguments:
                                    tool_call_args += tool_call.function.arguments
                
                # Check if we have a complete tool call
                if tool_call_id and chunk.choices[0].finish_reason == "tool_calls":
                    try:
                        args = json.loads(tool_call_args)
                        self.current_breach_info = BreachInfo(**args, conversation_complete=True)
                        yield json.dumps({
                            "type": "classification_complete", 
                            "data": self.current_breach_info.model_dump()
                        })
                    except Exception as e:
                        yield json.dumps({"type": "error", "data": f"Classification error: {str(e)} - Args: {tool_call_args}"})
                
        except Exception as e:
            yield json.dumps({"type": "error", "data": f"Error: {str(e)}"})

    async def continue_conversation(self, messages: List[Dict[str, str]], user_response: str) -> AsyncGenerator[str, None]:
        """Continue an existing conversation"""
        # Add user response to conversation history
        messages.append({"role": "user", "content": user_response})
        
        # Check if we need to force classification based on iteration count
        # Count user messages that are not the initial system prompt
        user_messages = [m for m in messages if m.get("role") == "user" and 
                        not m.get("content", "").startswith("I need help classifying")]
        iteration_count = len(user_messages)
        
        # Force classification after 4 user exchanges (including the current one we just added)
        if iteration_count >= 4:
            # Extract information from conversation history for forced classification
            conversation_text = "\n".join([f"{m['role']}: {m['content']}" for m in messages[-8:]])  # Last 8 messages for context
            
            forced_classification = self._make_forced_classification(conversation_text)
            self.current_breach_info = BreachInfo(**forced_classification, conversation_complete=True)
            
            yield json.dumps({"type": "message", "data": "Based on our conversation, I now have enough information to classify your GDPR breach case. Let me provide the classification:\n\n"})
            
            # Format the classification response
            classification_text = f"""**Final Classification:**

**Lawfulness of Processing:** {forced_classification['lawfulness_of_processing']}
**Data Subject Rights Compliance:** {forced_classification['data_subject_rights_compliance']}
**Risk Management and Safeguards:** {forced_classification['risk_management_and_safeguards']}
**Accountability and Governance:** {forced_classification['accountability_and_governance']}

**Case Summary:** {forced_classification['case_description']}

This classification is based on the information you've provided during our conversation. The case gathering is now complete."""
            
            yield json.dumps({"type": "message", "data": classification_text})
            yield json.dumps({
                "type": "classification_complete", 
                "data": self.current_breach_info.model_dump()
            })
            return
        
        try:
            stream = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                tools=self.tools,
                stream=True,
                temperature=0.3
            )

            response_text = ""
            tool_call_id = None
            tool_call_args = ""
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    response_text += content
                    yield json.dumps({"type": "message", "data": content})
                
                # Handle tool calls - they might come in multiple chunks
                if chunk.choices[0].delta.tool_calls:
                    for tool_call in chunk.choices[0].delta.tool_calls:
                        if tool_call.function:
                            if tool_call.function.name == "finalize_classification":
                                tool_call_id = tool_call.id
                                # Arguments might come in chunks, so accumulate them
                                if tool_call.function.arguments:
                                    tool_call_args += tool_call.function.arguments
                
                # Check if we have a complete tool call
                if tool_call_id and chunk.choices[0].finish_reason == "tool_calls":
                    try:
                        args = json.loads(tool_call_args)
                        self.current_breach_info = BreachInfo(**args, conversation_complete=True)
                        yield json.dumps({
                            "type": "classification_complete", 
                            "data": self.current_breach_info.model_dump()
                        })
                    except Exception as e:
                        yield json.dumps({"type": "error", "data": f"Classification error: {str(e)} - Args: {tool_call_args}"})
            
            # Add assistant response to conversation history
            if response_text:
                messages.append({"role": "assistant", "content": response_text})
                
        except Exception as e:
            yield json.dumps({"type": "error", "data": f"Error: {str(e)}"})

    def get_current_classification(self) -> Optional[BreachInfo]:
        """Get the current breach classification if complete"""
        if self.current_breach_info.conversation_complete:
            return self.current_breach_info
        return None

    def end_conversation(self):
        """Clean up the conversation"""
        # Reset the breach info for the next conversation
        self.current_breach_info = BreachInfo()

    def get_system_instructions_with_context(self, iteration_count: int) -> str:
        """Get system instructions with current iteration context"""
        max_iterations = 4
        context = f"\n\n**Current Status:** This is exchange {iteration_count}/{max_iterations} maximum."
        
        if iteration_count >= max_iterations:
            context += " **IMPORTANT: This is the final exchange. You MUST call finalize_classification now with your best assessment based on available information.**"
        elif iteration_count == max_iterations - 1:
            context += " **WARNING: This is the second-to-last exchange. Prepare to classify after the next user response.**"
        else:
            context += " Gather key information efficiently."
            
        return self.system_instructions + context
    
    def _make_forced_classification(self, conversation_text: str) -> dict:
        """Make a classification based on conversation history when iteration limit is reached"""
        # Default classifications - can be improved with better text analysis
        classification = {
            "case_description": "Data breach incident based on conversation history",
            "lawfulness_of_processing": "lawful_and_appropriate_basis",  # Default assumption
            "data_subject_rights_compliance": "partial_compliance",  # Conservative assumption
            "risk_management_and_safeguards": "insufficient_protection",  # Common case
            "accountability_and_governance": "partially_accountable"  # Conservative assumption
        }
        
        # Simple keyword-based classification improvements
        text_lower = conversation_text.lower()
        
        # Analyze lawfulness
        if any(word in text_lower for word in ["no basis", "unlawful", "no legal basis", "unauthorized"]):
            classification["lawfulness_of_processing"] = "no_valid_basis"
        elif any(word in text_lower for word in ["violation", "unfair", "not transparent"]):
            classification["lawfulness_of_processing"] = "lawful_but_principle_violation"
        elif any(word in text_lower for word in ["legitimate interest", "consent", "contract", "legal basis"]):
            classification["lawfulness_of_processing"] = "lawful_and_appropriate_basis"
            
        # Analyze data subject rights
        if any(word in text_lower for word in ["notified within", "contacted subjects", "informed customers"]):
            classification["data_subject_rights_compliance"] = "full_compliance"
        elif any(word in text_lower for word in ["failed to notify", "didn't inform", "no notification"]):
            classification["data_subject_rights_compliance"] = "non_compliance"
        elif any(word in text_lower for word in ["no rights triggered", "not applicable"]):
            classification["data_subject_rights_compliance"] = "not_triggered"
            
        # Analyze security measures
        if any(word in text_lower for word in ["comprehensive security", "advanced protection", "multiple safeguards"]):
            classification["risk_management_and_safeguards"] = "proactive_safeguards"
        elif any(word in text_lower for word in ["responded after", "reactive", "after the fact"]):
            classification["risk_management_and_safeguards"] = "reactive_only"
        elif any(word in text_lower for word in ["inadequate", "insufficient", "poor security", "no protection"]):
            classification["risk_management_and_safeguards"] = "insufficient_protection"
            
        # Analyze governance
        if any(word in text_lower for word in ["documented policies", "dpo", "data protection officer", "regular audits"]):
            classification["accountability_and_governance"] = "fully_accountable"
        elif any(word in text_lower for word in ["no policies", "no documentation", "no procedures"]):
            classification["accountability_and_governance"] = "not_accountable"
            
        # Extract case description from conversation
        user_messages = []
        for line in conversation_text.split('\n'):
            if line.startswith('user:'):
                user_messages.append(line[5:].strip())
        
        if user_messages:
            classification["case_description"] = " ".join(user_messages[:3])  # First 3 user messages
        
        return classification
