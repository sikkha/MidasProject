import sqlite3
import os
import requests
import re
import openai
from openai import OpenAI
from llm_handler import call_LLM


def create_narrative(cur):
    # Fetch the tweets from the database
    
    cur.execute('''
    SELECT T.item
    FROM PresentationTweets P
    JOIN Tweets T ON P.id = T.id
    ''')
    tweets = cur.fetchall()

    # Combine tweets into one text block for narrative generation
    tweets_combined = " ".join(tweet[0] for tweet in tweets)  # Assuming each tweet is in the first column of the fetch

    # Create prompt for AI to generate a narrative
    narrative_prompt = f"Create a cohesive narrative from the following tweets:\n{tweets_combined}"
    narrative = call_LLM("gemini-pro", narrative_prompt).strip()
    
    return narrative



def analyze_narrative(cur, narrative):
    context = """
    Metageopolitical knowledge graph:
    Overview
    An integrative framework that combines various geopolitical theories
    Seeks to address shortcomings and limitations of individual theories
    Draws inspiration from Alvin Toffler's "powershift" concept

    Powershift
        Foundation
            Inspired by The Three Sacred Treasures of Japan
                Valor (hard power)
                Wisdom (noopolitik)
                Benevolence (economic power)
            Recognizes the dynamic interplay of different powers in various domains

    Geopolitical Theories
        Heartland Theory (Sir Halford John Mackinder)
            Emphasizes the strategic significance of controlling the central landmass of Eurasia
        Rimland Theory (Nicholas John Spykman)
            Highlights the importance of controlling coastal regions for geopolitical advantage
        Geopolitical Implications and Hard Power (George Friedman)
            Expands upon the Heartland and Rimland theories, accounting for modern geopolitical realities
        Offensive Realism (John Joseph Mearsheimer)
            Concentrates on the pursuit of regional hegemony as a primary goal in international politics
        Neoliberalism
            Stresses the role of global institutions and economic power in shaping international relations
        Constructivism
            Views institutions as the result of human interactions and the construction of shared ideas

    Metageopolitical Framework Applications
        Inclusive Approach
            Integrates insights from multiple schools of thought for a more comprehensive understanding
        Multidimensional Analysis
            Takes into account military, economic, political, and social factors in assessing geopolitical situations
        Universal Application
            Adaptable to a wide range of international relations scenarios, enabling better predictions and strategic decisions

    Weekly scan section:
    """
    
    stylish_prompt = """
    Dear AI,

You are tasked with creating a professional and detailed geopolitical analysis report. The report should synthesize current global events into a cohesive narrative, applying theoretical frameworks to provide deeper insights into geopolitical dynamics. Below are the guidelines you must follow to ensure the report meets the highest standards of professionalism and analytical rigor.

Structure of the Report:

    Executive Summary:
        Provide a brief overview of the key findings and themes covered in the report.

    Introduction:
        Introduce the scope of the report and outline the geopolitical theories that will be applied.

    Main Analysis:
        Divide this section into sub-sections, each focusing on a different geopolitical event or theme.
        For each sub-section:
            Describe the event or trend in detail.
            Apply relevant geopolitical theories to analyze the event.
            Discuss the implications of the event on international relations and global power dynamics.

    Conclusion:
        Summarize the main insights derived from the analysis.
        Highlight potential future developments and recommend strategies for stakeholders.

    References:
        Cite all sources and references used in crafting the report to enhance credibility.

Content Requirements:

    Ensure that the analysis is data-driven and includes up-to-date information.
    Use precise language that is appropriate for an academic and policy-making audience.
    Integrate quotes from experts or relevant figures where applicable to support your arguments.

Style and Formatting Guidelines:

    Utilize formal academic language throughout the report.
    Employ clear and concise sentences to enhance readability.
    Make use of bullet points, tables, and graphs to present data effectively.
    Apply headers and subheaders to organize the content logically.
    Ensure that all sections are well-aligned and uniformly formatted.

Additional Notes:

    Pay special attention to the clarity of the executive summary, as it should encapsulate the essence of the report succinctly.
    In the conclusion, be forward-looking and speculate on how the situations might evolve based on the analyzed data.

Please begin your work by outlining the key points for each section and proceed to fill in detailed content following the structure provided. The final output should be comprehensive, insightful, and meticulously formatted.
    """
    
    # Create prompt for AI to analyze the narrative
    analysis_prompt = f"Using following knowledge graph as your own knowledge, {context}\nAnd make geopolitical report from the following material:\n\n{narrative}, by usint this style of writing:\n\n {stylish_prompt}"
    analysis_result = call_LLM("gpt4", analysis_prompt).strip()
    
    return analysis_result

def main():
    # Connect to the SQLite database
    conn = sqlite3.connect('tweets.db')
    cur = conn.cursor()

    try:
        # Create a narrative from tweets
        narrative = create_narrative(cur)
        #print("Narrative Created:\n", narrative)

        # Analyze the narrative
        analysis = analyze_narrative(cur, narrative)
        print("Narrative Analysis:\n", analysis)

    finally:
        # Close the database connection
        conn.close()

if __name__ == "__main__":
    main()



