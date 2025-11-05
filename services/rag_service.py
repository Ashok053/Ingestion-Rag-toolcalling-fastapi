from services.embeddings import generate_embeddings
from services.vectorsStore import search_similar_chunks
from core.configuration import settings
from typing import List, Dict, Tuple
from services.llm_service import llm_service
class CustomRAG:
    """ RAG service using LLM without using Retrieval QA Chain """

    @staticmethod
    def retrieve_context(query: str, top_k: int = 3) -> Tuple[str, List[Dict]]:
        """Retrieve related chunks"""
        query_chunks = [{'text': query}]
        query_embedding = generate_embeddings(query_chunks)[0]

        # Search in Qdrant
        results = search_similar_chunks(
            query_embedding=query_embedding,
            top_k=top_k,
            collection_name=settings.QDRANT_COLLECTION
        )

        if results:
            context = "\n\n".join([
                f"[Source {i + 1}] (Relevance: {r['score']:.2f})\n{r['text']}"
                for i, r in enumerate(results)
            ])
        else:
            context = "No relevant information found in documents."
        return context, results

    @staticmethod
    def build_prompt(query: str, context: str, chat_history: str = "") -> str:
        """Build prompt for LLM"""
        prompt = f"You are a helpful assistant answering questions based on provided documents.\nContext from documents:\n{context}\n"

        if chat_history:
            prompt += f"Previous conversation:\n{chat_history}\n"

        prompt += (
            f"Current question: {query}\n"
            "Instruction: answer based only on provided context, "
            "if the context does not contain relevant information, say sorry, "
            "be concise and helpful. "
            "If asked about booking/scheduling, guide them to use the booking API."
        )

        return prompt

    @staticmethod
    def generate_answer(query: str, context: str, chat_history: str = "") -> str:
        """Generate answer using LLM"""
        booking_keywords = ['book', 'interview', 'schedule', 'appointment']

        if any(keyword in query.lower() for keyword in booking_keywords):
            return (
                "I can help you to book an interview. Please use the booking endpoint:\n\n"
                "POST /api/bookings/\n\n"
                "Provide:\n"
                "- name: your full name\n"
                "- email: your email address\n"
                "- date: Preferred date (YYYY-MM-DD)\n"
                "- time: Preferred time (HH:MM)\n"
                "Or tell me your details and I'll help you format the request!"
            )

        prompt = CustomRAG.build_prompt(query, context, chat_history)
        answer = llm_service.generate(
            prompt=prompt,
            max_tokens=500,
            temperature=0.7
        )
        return answer

    @staticmethod
    def answer_query(query: str, chat_history: str = "") -> Tuple[str, List[str]]:
        """Complete RAG pipeline"""
        context, results = CustomRAG.retrieve_context(query, top_k=3)
        answer = CustomRAG.generate_answer(query, context, chat_history)
        sources = [r['text'][:150] + "..." for r in results] if results else []
        return answer, sources
