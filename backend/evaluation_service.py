from agents import Agent, GuardrailFunctionOutput, InputGuardrail, InputGuardrailTripwireTriggered, Runner
from openai import OpenAI
from models import CaseDescription, GdprParagraphList

articles ="Art. 5, 6, 10, 13, 17, 25 , 32, 33, 34, 35 and 44 of the GDPR"


guardrail_agent = Agent(
    name="Guardrail check",
    instructions="Check if the prompt is about evaluating a data breach.",
    output_type=CaseDescription,
)

evaluation_agent = Agent(
    name="Evaluator",
    handoff_description="Specialist agent for evaluating data breach cases",
    instructions="You provide evaluate databreaches against GDPR articles.",
    output_type=GdprParagraphList
)

async def case_guardrail(ctx, agent, input_data):
    result = await Runner.run(guardrail_agent, input_data, context=ctx.context)
    final_output = result.final_output_as(CaseDescription)
    return GuardrailFunctionOutput(
        output_info=final_output,
        tripwire_triggered=not final_output.is_case_description,
    )

triage_agent = Agent(
    name="Triage Agent",
    instructions="You are a data breach expert and use the evaluation agent to evaluate data breaches",
    handoffs=[evaluation_agent],
    input_guardrails=[
        InputGuardrail(guardrail_function=case_guardrail),
    ],
)



class EvaluationService:
    def __init__(self, api_key):
        if not api_key:
            raise ValueError("OpenAI API key is not provided.")
        self.openai = OpenAI(api_key=api_key)

    # def get_evaluation(self, case_description):
    #     try:
    #         prompt = f"""Our company had a data breach. Here's what happend: {case_description}. Please calculate the probability of us violating the following GDPR articles: {articles} and the approximate fine that we can expect. For each paragraph, assign the fitting classificcation. """

    #         response = self.openai.responses.parse(
    #             model="gpt-4o-2024-08-06",
    #             tools=[{
    #                 "type": "web_search_preview",
    #                 "search_context_size": "low",
    #             }],
    #             input=[
    #                 {"role": "system", "content": "You are an GDPR Expert that can help asses the risk of data breaches."},
    #                 {"role": "user", "content": prompt}
    #             ],
    #             text_format=GdprParagraphList,
    #         )
    #         return response.output_parsed

    #     except Exception as e:
    #         print(f"An error occured")
    #         return None
        
    async def get_evaluation(self, case_description):
        prompt = f"""Our company had a data breach. Here's what happend: {case_description}. Please calculate the probability of us violating the following GDPR articles: {articles} and the approximate fine that we can expect. For each paragraph, assign the fitting classificcation. """

        try:
            result = await Runner.run(triage_agent, prompt)
            return result.final_output

        except InputGuardrailTripwireTriggered as e:
            print("Guardrail blocked this input:", e)

