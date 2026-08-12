"""
Wrapper fino sobre o SDK oficial da OCI (oci.generative_ai_inference) para
gerar embeddings de texto e respostas de chat usando os modelos gerenciados
da OCI Generative AI.

Requer:
  - Um arquivo ~/.oci/config válido (gerado pela CLI da OCI ou pelo console)
    OU as variáveis de ambiente equivalentes, conforme a documentação da OCI:
    https://docs.oracle.com/en-us/iaas/Content/API/Concepts/sdkconfig.htm
  - Acesso liberado ao serviço "Generative AI" no compartment configurado.

Observação: os nomes de classes do SDK (EmbedTextDetails, ChatDetails,
GenericChatRequest, etc.) podem variar entre versões do pacote `oci`.
Se algum atributo não existir na sua versão instalada, confira a versão
mais recente do SDK com `pip show oci` e a documentação oficial.
"""
from typing import List

import oci

from app.config import (
    OCI_CONFIG_PROFILE,
    OCI_COMPARTMENT_ID,
    OCI_GENAI_ENDPOINT,
    EMBED_MODEL_ID,
    CHAT_MODEL_ID,
)

SYSTEM_PROMPT = (
    "Você é um assistente de atendimento ao cliente da NovaShop. "
    "Responda SOMENTE com base no CONTEXTO fornecido abaixo. "
    "Se a resposta não estiver no contexto, diga claramente que não possui "
    "essa informação e sugira que o cliente fale com o atendimento humano. "
    "Seja objetivo e responda em português do Brasil."
)


class OCIGenAIClient:
    def __init__(self):
        config = oci.config.from_file(profile_name=OCI_CONFIG_PROFILE)
        self.client = oci.generative_ai_inference.GenerativeAiInferenceClient(
            config=config,
            service_endpoint=OCI_GENAI_ENDPOINT,
            retry_strategy=oci.retry.NoneRetryStrategy(),
            timeout=(10, 240),
        )
        self.compartment_id = OCI_COMPARTMENT_ID

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Gera embeddings para uma lista de textos."""
        details = oci.generative_ai_inference.models.EmbedTextDetails(
            inputs=texts,
            serving_mode=oci.generative_ai_inference.models.OnDemandServingMode(
                model_id=EMBED_MODEL_ID
            ),
            compartment_id=self.compartment_id,
            truncate="END",
        )
        response = self.client.embed_text(details)
        return response.data.embeddings

    def chat(self, question: str, context_chunks: List[str]) -> str:
        """Gera uma resposta de chat com base nos chunks de contexto recuperados."""
        context_text = "\n\n---\n\n".join(context_chunks)
        user_message = f"CONTEXTO:\n{context_text}\n\nPERGUNTA DO CLIENTE:\n{question}"

        system_content = oci.generative_ai_inference.models.TextContent(text=SYSTEM_PROMPT)
        system_message = oci.generative_ai_inference.models.Message(
            role="SYSTEM", content=[system_content]
        )

        user_content = oci.generative_ai_inference.models.TextContent(text=user_message)
        user_msg = oci.generative_ai_inference.models.Message(
            role="USER", content=[user_content]
        )

        chat_request = oci.generative_ai_inference.models.GenericChatRequest(
            api_format=oci.generative_ai_inference.models.BaseChatRequest.API_FORMAT_GENERIC,
            messages=[system_message, user_msg],
            max_tokens=600,
            temperature=0.2,
            top_p=0.9,
        )

        chat_details = oci.generative_ai_inference.models.ChatDetails(
            serving_mode=oci.generative_ai_inference.models.OnDemandServingMode(
                model_id=CHAT_MODEL_ID
            ),
            chat_request=chat_request,
            compartment_id=self.compartment_id,
        )

        response = self.client.chat(chat_details)
        return response.data.chat_response.choices[0].message.content[0].text
