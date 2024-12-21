from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
import json

# Define ministries and their functions
ministries = {
    "Ministry of Finance": "Manages public finances, national budget, taxation, fiscal policy, and economic growth initiatives. Oversees state revenues and expenditures.",
    "Ministry of Health": "Oversees public health services, hospitals, health education, disease prevention, and health policy implementation.",
    "Ministry of Education": "Responsible for developing and managing the education system, including schools, universities, curriculum standards, and educational policies.",
    "Ministry of Defense": "Manages national defense, armed forces, military policy, and often disaster response capabilities.",
    "Ministry of Foreign Affairs": "Handles international relations, diplomacy, treaties, and representation in foreign countries and international organizations.",
    "Ministry of Interior (or Home Affairs)": "Responsible for internal security, law enforcement, immigration, civil defense, and local governance.",
    "Ministry of Justice": "Oversees the judicial system, legal policies, correctional facilities, and law reform initiatives.",
    "Ministry of Agriculture": "Focuses on agricultural development, food security, rural development, and support for farmers.",
    "Ministry of Environment": "Manages environmental conservation, climate change policy, wildlife protection, and sustainable development.",
    "Ministry of Transport": "Oversees transportation infrastructure (roads, railways, airports, ports) and transportation safety regulations.",
    "Ministry of Labor (or Employment)": "Focuses on employment policies, labor rights, workplace safety, and skill development.",
    "Ministry of Energy": "Manages energy resources, policies, and sustainability efforts, including renewable energy initiatives.",
    "Ministry of Industry and Trade": "Promotes industrial growth, international trade, export/import regulations, and support for businesses.",
    "Ministry of Housing (or Urban Development)": "Addresses urban planning, housing development, and public infrastructure in cities and rural areas.",
    "Ministry of Culture": "Promotes cultural heritage, arts, and national identity. Manages museums, cultural festivals, and historical preservation.",
    "Ministry of Tourism": "Develops tourism policies, promotes the country as a travel destination, and oversees tourism infrastructure.",
    "Ministry of Social Welfare": "Provides social services, welfare programs, poverty alleviation, and support for marginalized groups.",
    "Ministry of Science and Technology": "Promotes scientific research, technological development, and innovation in various sectors.",
    "Ministry of Telecommunications/IT": "Manages communication infrastructure, internet policies, and IT development strategies.",
    "Ministry of Youth and Sports": "Focuses on youth development programs and the promotion of sports and physical activities.",
    "Ministry of Public Works": "Manages public infrastructure projects such as roads, bridges, and government buildings.",
    "Ministry of Immigration (or Citizenship)": "Oversees immigration, citizenship, and residency policies.",
    "Ministry of Defense Production": "Oversees the production and procurement of military equipment and supplies (where relevant).",
    "Ministry of Water Resources": "Manages water resources, irrigation systems, and water conservation efforts.",
}

# Initialize the LLM
llm = OpenAI(model="text-davinci-003")

# Define the prompt template
prompt_template = PromptTemplate(
    input_variables=["ministry", "function"],
    template="Generate 5 unique user queries related to the {ministry} and its functions. {function}",
)

# Generate synthetic data
synthetic_data = []
for ministry, function in ministries.items():
    prompt = prompt_template.format(ministry=ministry, function=function)
    response = llm(prompt)
    queries = response.split("\n")  # Split the LLM's response into individual queries
    for query in queries:
        query = query.strip()
        if query:  # Avoid empty lines
            synthetic_data.append({"query": query, "ministry": ministry})

# Save the dataset as labeled JSON
with open("synthetic_dataset.json", "w") as f:
    json.dump(synthetic_data, f, indent=4)

print("Synthetic dataset saved as 'synthetic_dataset.json'.")
