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
            
            return f"""**Perfect! I've classified your case as follows:**

**Case Description:** {case_description}

**Classification Complete:**
- **Lawfulness of Processing:** {lawfulness_of_processing}
- **Data Subject Rights Compliance:** {data_subject_rights_compliance}  
- **Risk Management and Safeguards:** {risk_management_and_safeguards}
- **Accountability and Governance:** {accountability_and_governance}

This classification will help with subsequent analysis and fine prediction. The case gathering is now complete and you will be redirected to the case analysis dashboard."""
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
            tool_calls = {}  # Store tool calls by ID
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    response_text += content
                    yield json.dumps({"type": "message", "data": content})
                
                # Handle tool calls - they might come in multiple chunks
                if chunk.choices[0].delta.tool_calls:
                    for tool_call in chunk.choices[0].delta.tool_calls:
                        if tool_call.id:
                            if tool_call.id not in tool_calls:
                                tool_calls[tool_call.id] = {
                                    "name": "",
                                    "arguments": ""
                                }
                            
                            if tool_call.function:
                                if tool_call.function.name:
                                    tool_calls[tool_call.id]["name"] = tool_call.function.name
                                if tool_call.function.arguments:
                                    tool_calls[tool_call.id]["arguments"] += tool_call.function.arguments
                
                # Check if we have a complete tool call when the stream finishes
                if chunk.choices[0].finish_reason == "tool_calls":
                    print(f"[START] Tool calls detected: {tool_calls}")  # Debug logging
                    for tool_call_id, tool_data in tool_calls.items():
                        print(f"[START] Processing tool call {tool_call_id}: {tool_data}")  # Debug logging
                        if tool_data["name"] == "finalize_classification" and tool_data["arguments"]:
                            try:
                                print(f"[START] Attempting to parse: {tool_data['arguments']}")  # Debug logging
                                args = json.loads(tool_data["arguments"])
                                self.current_breach_info = BreachInfo(**args, conversation_complete=True)
                                yield json.dumps({
                                    "type": "classification_complete", 
                                    "data": self.current_breach_info.model_dump()
                                })
                            except json.JSONDecodeError as e:
                                print(f"[START] JSON decode error: {e}")  # Debug logging
                                yield json.dumps({"type": "error", "data": f"JSON parsing error: {str(e)} - Args: '{tool_data['arguments']}'"})
                            except Exception as e:
                                print(f"[START] Classification error: {e}")  # Debug logging
                                yield json.dumps({"type": "error", "data": f"Classification error: {str(e)} - Args: '{tool_data['arguments']}'"})
                        elif tool_data["name"] == "finalize_classification" and not tool_data["arguments"]:
                            print("[START] Tool call detected but no arguments received")  # Debug logging
                            yield json.dumps({"type": "error", "data": "Tool call detected but no arguments received"})
            
            # Final check for any accumulated tool calls
            for tool_call_id, tool_data in tool_calls.items():
                if tool_data["name"] == "finalize_classification" and tool_data["arguments"] and not self.current_breach_info.conversation_complete:
                    try:
                        print(f"[START-FINAL] Final attempt to parse: {tool_data['arguments']}")  # Debug logging
                        args = json.loads(tool_data["arguments"])
                        self.current_breach_info = BreachInfo(**args, conversation_complete=True)
                        yield json.dumps({
                            "type": "classification_complete", 
                            "data": self.current_breach_info.model_dump()
                        })
                    except Exception as e:
                        print(f"[START-FINAL] Final parse error: {e}")  # Debug logging
                        yield json.dumps({"type": "error", "data": f"Final classification error: {str(e)} - Args: '{tool_data['arguments']}'"})
                
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
            try:
                # Extract information from conversation history for forced classification
                conversation_text = "\n".join([f"{m['role']}: {m['content']}" for m in messages[-8:]])  # Last 8 messages for context
                
                forced_classification = self._make_forced_classification(conversation_text)
                self.current_breach_info = BreachInfo(**forced_classification, conversation_complete=True)
                
                yield json.dumps({"type": "message", "data": "Based on our conversation, I now have enough information to classify your GDPR breach case. Let me provide the classification:\n\n"})
                
                # Format the classification response
                classification_text = f"""**Final Classification Complete:**

**Lawfulness of Processing:** {forced_classification['lawfulness_of_processing']}
**Data Subject Rights Compliance:** {forced_classification['data_subject_rights_compliance']}
**Risk Management and Safeguards:** {forced_classification['risk_management_and_safeguards']}
**Accountability and Governance:** {forced_classification['accountability_and_governance']}

**Case Summary:** {forced_classification['case_description']}

This classification is based on the information provided during our conversation. The case gathering is now complete and you will be redirected to the case analysis dashboard."""
                
                yield json.dumps({"type": "message", "data": classification_text})
                yield json.dumps({
                    "type": "classification_complete", 
                    "data": self.current_breach_info.model_dump()
                })
                return
            except Exception as e:
                yield json.dumps({"type": "error", "data": f"Forced classification error: {str(e)}"})
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
            tool_calls = {}  # Store tool calls by ID
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    response_text += content
                    yield json.dumps({"type": "message", "data": content})
                
                # Handle tool calls - they might come in multiple chunks
                if chunk.choices[0].delta.tool_calls:
                    for tool_call in chunk.choices[0].delta.tool_calls:
                        if tool_call.id:
                            if tool_call.id not in tool_calls:
                                tool_calls[tool_call.id] = {
                                    "name": "",
                                    "arguments": ""
                                }
                            
                            if tool_call.function:
                                if tool_call.function.name:
                                    tool_calls[tool_call.id]["name"] = tool_call.function.name
                                if tool_call.function.arguments:
                                    tool_calls[tool_call.id]["arguments"] += tool_call.function.arguments
                
                # Check if we have a complete tool call when the stream finishes
                if chunk.choices[0].finish_reason == "tool_calls":
                    print(f"[CONTINUE] Tool calls detected: {tool_calls}")  # Debug logging
                    for tool_call_id, tool_data in tool_calls.items():
                        print(f"[CONTINUE] Processing tool call {tool_call_id}: {tool_data}")  # Debug logging
                        if tool_data["name"] == "finalize_classification" and tool_data["arguments"]:
                            try:
                                print(f"[CONTINUE] Attempting to parse: {tool_data['arguments']}")  # Debug logging
                                args = json.loads(tool_data["arguments"])
                                self.current_breach_info = BreachInfo(**args, conversation_complete=True)
                                yield json.dumps({
                                    "type": "classification_complete", 
                                    "data": self.current_breach_info.model_dump()
                                })
                            except json.JSONDecodeError as e:
                                print(f"[CONTINUE] JSON decode error: {e}")  # Debug logging
                                yield json.dumps({"type": "error", "data": f"JSON parsing error: {str(e)} - Args: '{tool_data['arguments']}'"})
                            except Exception as e:
                                print(f"[CONTINUE] Classification error: {e}")  # Debug logging
                                yield json.dumps({"type": "error", "data": f"Classification error: {str(e)} - Args: '{tool_data['arguments']}'"})
                        elif tool_data["name"] == "finalize_classification" and not tool_data["arguments"]:
                            print("[CONTINUE] Tool call detected but no arguments received")  # Debug logging
                            yield json.dumps({"type": "error", "data": "Tool call detected but no arguments received"})
            
            # Final check for any accumulated tool calls
            for tool_call_id, tool_data in tool_calls.items():
                if tool_data["name"] == "finalize_classification" and tool_data["arguments"] and not self.current_breach_info.conversation_complete:
                    try:
                        print(f"[CONTINUE-FINAL] Final attempt to parse: {tool_data['arguments']}")  # Debug logging
                        args = json.loads(tool_data["arguments"])
                        self.current_breach_info = BreachInfo(**args, conversation_complete=True)
                        yield json.dumps({
                            "type": "classification_complete", 
                            "data": self.current_breach_info.model_dump()
                        })
                    except Exception as e:
                        print(f"[CONTINUE-FINAL] Final parse error: {e}")  # Debug logging
                        yield json.dumps({"type": "error", "data": f"Final classification error: {str(e)} - Args: '{tool_data['arguments']}'"})
            
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
            context += " **IMPORTANT: This is the final exchange. You MUST call the finalize_classification function now with your best assessment based on available information. Do not ask more questions.**"
        elif iteration_count == max_iterations - 1:
            context += " **WARNING: This is the second-to-last exchange. After the user's next response, you must classify immediately.**"
        else:
            context += " Gather key information efficiently. Remember to call finalize_classification when you have sufficient information."
            
        return self.system_instructions + context
    
    async def _make_forced_classification(self, conversation_text: str) -> dict:
        """Make a classification based on conversation history using OpenAI structured output"""
        try:
            # Create a prompt for classification analysis
            classification_prompt = f"""
            Based on the following conversation about a GDPR breach incident, please provide a comprehensive classification across the 4 key dimensions.

            Conversation History:
            {conversation_text}

            Please analyze the conversation and classify the breach case across these dimensions:

            1. **Lawfulness of Processing** - Choose one:
               - lawful_and_appropriate_basis: Processing had clear legal basis and was appropriate
               - lawful_but_principle_violation: Legal basis existed but violated GDPR principles
               - no_valid_basis: No valid legal basis for processing
               - exempt_or_restricted: Processing was exempt from GDPR or had restricted applicability

            2. **Data Subject Rights Compliance** - Choose one:
               - full_compliance: All relevant data subject rights were properly handled
               - partial_compliance: Some rights were handled but with deficiencies
               - non_compliance: Failed to respect data subject rights
               - not_triggered: No data subject rights were triggered in this case

            3. **Risk Management and Safeguards** - Choose one:
               - proactive_safeguards: Had comprehensive preventive security measures
               - reactive_only: Only responded after incident occurred
               - insufficient_protection: Inadequate security measures in place
               - not_applicable: Risk management not relevant to this case

            4. **Accountability and Governance** - Choose one:
               - fully_accountable: Complete documentation, policies, and governance
               - partially_accountable: Some accountability measures but gaps exist
               - not_accountable: Failed to demonstrate compliance accountability
               - not_required: Accountability requirements didn't apply

            Provide a comprehensive case description summarizing the incident and your classification rationale.
            """

            # Use OpenAI with structured output to ensure proper formatting
            response = await self.client.chat.completions.create(
                model="gpt-4o-2024-08-06",
                messages=[
                    {"role": "system", "content": "You are an expert GDPR case analysis assistant. Analyze the conversation history and provide a structured classification of the breach incident based on the 4 key dimensions. Make reasonable inferences where information is incomplete."},
                    {"role": "user", "content": classification_prompt}
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "breach_classification",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "case_description": {
                                    "type": "string",
                                    "description": "Complete description of the breach case based on conversation"
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
                            "required": ["case_description", "lawfulness_of_processing", "data_subject_rights_compliance", "risk_management_and_safeguards", "accountability_and_governance"],
                            "additionalProperties": False
                        }
                    }
                }
            )
            
            # Parse the structured response
            classification_data = json.loads(response.choices[0].message.content)
            return classification_data
            
        except Exception as e:
            print(f"Error in forced classification: {e}")
            # Fallback to simple classification
            return {
                "case_description": "Data breach incident based on conversation history",
                "lawfulness_of_processing": "lawful_and_appropriate_basis",
                "data_subject_rights_compliance": "partial_compliance", 
                "risk_management_and_safeguards": "insufficient_protection",
                "accountability_and_governance": "partially_accountable"
            }
