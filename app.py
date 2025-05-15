import streamlit as st
import folium
from streamlit_folium import st_folium
from PyPDF2 import PdfReader
import yaml
from folium.plugins import Geocoder
import json
from math import radians, sin, cos, sqrt, atan2
import heapq
from datetime import datetime, time
import polyline
import googlemaps

import time
import requests
import subprocess
import webbrowser

CONFIG_PATH = r"config.yaml"
with open(CONFIG_PATH) as file:
    data = yaml.load(file, Loader=yaml.FullLoader)
    api_key = data['OPENAI_API_KEY']
    PERPLEX_API = data['PERPLEX_API']
    gmaps_api_key = data['GOOGLE_MAPS_API_KEY']

gmaps = googlemaps.Client(key=gmaps_api_key)

def run_chainlit_app():
    subprocess.Popen(["chainlit", "run", "../chainlit-chatbot/app.py", "-w"])


def extract_text_from_pdf(pdf_file):
    try:
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error extracting PDF text: {str(e)}")
        return None
    
def extract_skills(resume_text):
    try:
        url = "https://api.perplexity.ai/chat/completions"

        headers = {
            "Authorization": f"Bearer {PERPLEX_API}",
            "Content-Type": "application/json"
        }
        prompt = (
            f"You are an AI bot designed to extract technical skills from resumes. "
            f"Extract only the technical skills from the following text and return them as a comma-separated list: \n"
            f"{resume_text}"
        )

        payload = {
            "model": "llama-3.1-sonar-small-128k-online",
            "messages": [
                {"role": "system", "content": "Be precise and concise."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 1500,
            "temperature": 0.0,
            "top_p": 0.9,
            "search_domain_filter": ["perplexity.ai"],
            "return_images": False,
            "return_related_questions": False,
            "search_recency_filter": "month",
            "top_k": 0,
            "stream": False,
            "presence_penalty": 0,
            "frequency_penalty": 1
        }

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            response_data = response.json()
            skills = response_data["choices"][0].get("message", {}).get("content", "")
            return [skill.strip() for skill in skills.split(",")]
        else:
            st.error(f"Error extracting skills: {response.status_code}, {response.text}")
            return []
    except Exception as e:
        st.error(f"Error extracting skills: {str(e)}")
        return []
    

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

class Node:
    def __init__(self, company, g, h, w_proximity, w_skills):
        self.company = company
        self.g = g 
        self.h = h  
        self.f = w_proximity * g + w_skills * h

    def __lt__(self, other):
        return self.f < other.f

def a_star_algorithm(companies, user_location, user_skills, w_proximity, w_skills):
    open_set = []
    closed_set = set()
    results = []

    user_skills = set([skill.lower() for skill in user_skills])
    
    for company in companies:
        lat, lon = company['latitude'], company['longitude']
        distance = haversine_distance(user_location[0], user_location[1], lat, lon)
        
        company_skills = set([skill.lower() for skill in company.get('skills', [])])
        skill_match_score = len(user_skills & company_skills) / len(user_skills) if len(user_skills) > 0 else 0
        h = 1 - skill_match_score

        if skill_match_score > 0:
            node = Node(company, distance, h, w_proximity, w_skills)
            heapq.heappush(open_set, node)

    while open_set and len(results) < 5:
        current_node = heapq.heappop(open_set)
        company = current_node.company
        
        if company['Company Name'] not in closed_set:
            closed_set.add(company['Company Name'])
            results.append({
                'company': company,
                'distance': current_node.g,
                'final_score': current_node.f
            })

    results.sort(key=lambda x: x['final_score'])
    return results

def main():
    st.title("Resume-Based Internship Finder")

    
    if 'location' not in st.session_state:
        st.session_state.location = None
    if 'skills' not in st.session_state:
        st.session_state.skills = None
    if 'resume_processed' not in st.session_state:
        st.session_state.resume_processed = False
    if 'route_shown' not in st.session_state:
        st.session_state.route_shown = False
    if 'current_route' not in st.session_state:
        st.session_state.current_route = None

    
    st.header("1. Upload Your Resume")
    uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])

    if uploaded_file:
        if not st.session_state.resume_processed:
            with st.spinner("Processing resume..."):
                resume_text = extract_text_from_pdf(uploaded_file)
                if resume_text:
                    st.session_state.skills = extract_skills(resume_text)
                    st.session_state.resume_processed = True

        if st.session_state.skills:
            st.success("Resume processed successfully!")
            st.write("**Extracted Skills:**")
            st.write(", ".join(st.session_state.skills))

    
    st.header("2. Set Matching Preferences")
    w_proximity = st.slider("Weight for Proximity", 0.0, 1.0, 0.5,
                          help="Higher value gives more importance to distance")
    w_skills = st.slider("Weight for Skills Match", 0.0, 1.0, 0.5,
                        help="Higher value gives more importance to skill matching")

   
    st.header("3. Select Your Location")
    st.write("Click on the map to set your location or use the search box")
    
    
    m = folium.Map(location=[25.276987, 55.296249], zoom_start=11)
    Geocoder(add_marker=False).add_to(m)
    m.add_child(folium.LatLngPopup())
    
    if st.session_state.location:
        folium.Marker(
            [st.session_state.location['lat'], st.session_state.location['lng']],
            popup="Your Location",
            icon=folium.Icon(color='red')
        ).add_to(m)

    map_data = st_folium(m, height=400, width=700)
    
    if map_data['last_clicked']:
        st.session_state.location = map_data['last_clicked']
        # st.experimental_rerun()

   
    if st.session_state.location:
        st.write(f"Selected Location: {st.session_state.location['lat']:.6f}, {st.session_state.location['lng']:.6f}")

    
    if st.session_state.location and st.session_state.skills:
        st.header("Matching Internships")
        
        
        internships = [
            {'Company Name': 'XYZ Tech', 'title': 'Internship 1', 'latitude': 25.197525, 'longitude': 55.274288, 'skills': ['Python', 'Data Analysis']},
            {'Company Name': 'ABC Solutions', 'title': 'Internship 2', 'latitude': 25.234511, 'longitude': 55.324905, 'skills': ['Machine Learning', 'Data Analysis']},
            {'Company Name': 'InnovAI', 'title': 'Internship 3', 'latitude': 25.245789, 'longitude': 55.307501, 'skills': ['Python', 'Web Development']},
            {'Company Name': 'TechMasters', 'title': 'Internship 4', 'latitude': 25.206789, 'longitude': 55.325789, 'skills': ['Java', 'APIs']},
            {'Company Name': 'Creative Web', 'title': 'Internship 5', 'latitude': 25.218946, 'longitude': 55.322089, 'skills': ['HTML', 'CSS']},
            {'Company Name': 'Cloud Services', 'title': 'Internship 6', 'latitude': 25.227089, 'longitude': 55.310123, 'skills': ['Cloud Computing', 'Python']},
            {'Company Name': 'ProdSmart', 'title': 'Internship 7', 'latitude': 25.200123, 'longitude': 55.301234, 'skills': ['Data Analysis', 'Machine Learning']},
            {'Company Name': 'DesignHub', 'title': 'Internship 8', 'latitude': 25.201456, 'longitude': 55.295678, 'skills': ['UX Design', 'Prototyping']},
            {'Company Name': 'DataWise', 'title': 'Internship 9', 'latitude': 25.235678, 'longitude': 55.280123, 'skills': ['SQL', 'Data Analysis']},
            {'Company Name': 'SecureNet', 'title': 'Internship 10', 'latitude': 25.203456, 'longitude': 55.275678, 'skills': ['Cybersecurity', 'Networking']},
            {'Company Name': 'Future Innovations', 'title': 'Internship 11', 'latitude': 25.225678, 'longitude': 55.290123, 'skills': ['Deep Learning', 'Python']},
            {'Company Name': 'Smart Systems', 'title': 'Internship 12', 'latitude': 25.240789, 'longitude': 55.290456, 'skills': ['Java', 'Machine Learning']},
            {'Company Name': 'Digital Ventures', 'title': 'Internship 13', 'latitude': 25.222345, 'longitude': 55.301789, 'skills': ['React', 'APIs']},
            {'Company Name': 'NextGen Tech', 'title': 'Internship 14', 'latitude': 25.207234, 'longitude': 55.325123, 'skills': ['Kubernetes', 'Docker']},
            {'Company Name': 'Insight Analytics', 'title': 'Internship 15', 'latitude': 25.230456, 'longitude': 55.307890, 'skills': ['Data Visualization', 'Python']},
            {'Company Name': 'Visionary Labs', 'title': 'Internship 16', 'latitude': 25.215678, 'longitude': 55.310789, 'skills': ['TensorFlow', 'Deep Learning']},
            {'Company Name': 'AI Solutions', 'title': 'Internship 17', 'latitude': 25.205678, 'longitude': 55.298456, 'skills': ['Machine Learning', 'Research']},
            {'Company Name': 'TechHive', 'title': 'Internship 18', 'latitude': 25.238901, 'longitude': 55.270123, 'skills': ['Web Development', 'HTML']},
            {'Company Name': 'Data Solutions', 'title': 'Internship 19', 'latitude': 25.198765, 'longitude': 55.281234, 'skills': ['Python', 'Data Analysis']},
            {'Company Name': 'Web Wizards', 'title': 'Internship 20', 'latitude': 25.219123, 'longitude': 55.276123, 'skills': ['JavaScript', 'React']},
            {'Company Name': 'Clever Coders', 'title': 'Internship 21', 'latitude': 25.232345, 'longitude': 55.295678, 'skills': ['APIs', 'Node.js']},
            {'Company Name': 'SoftWare House', 'title': 'Internship 22', 'latitude': 25.228567, 'longitude': 55.286543, 'skills': ['Cloud Computing', 'Python']},
            {'Company Name': 'Genius Minds', 'title': 'Internship 23', 'latitude': 25.212345, 'longitude': 55.293678, 'skills': ['Data Analysis', 'SQL']},
            {'Company Name': 'Peak Performers', 'title': 'Internship 24', 'latitude': 25.206123, 'longitude': 55.278901, 'skills': ['Cybersecurity', 'Networking']},
            {'Company Name': 'Elite Solutions', 'title': 'Internship 25', 'latitude': 25.230456, 'longitude': 55.290678, 'skills': ['Machine Learning', 'Data Analysis']}
        ]

        user_loc = [st.session_state.location['lat'], st.session_state.location['lng']]
        matches = a_star_algorithm(internships, user_loc, st.session_state.skills, w_proximity, w_skills)

        if matches:
            results_map = folium.Map(location=user_loc, zoom_start=12)
            
            folium.Marker(
                user_loc,
                popup="Your Location",
                icon=folium.Icon(color='red')
            ).add_to(results_map)
            
            for match in matches:
                company = match['company']
                folium.Marker(
                    [company['latitude'], company['longitude']],
                    popup=f"{company['title']} at {company['Company Name']}<br>Distance: {match['distance']:.2f} km<br>Score: {match['final_score']:.2f}",
                    icon=folium.Icon(color='blue')
                ).add_to(results_map)
            
            st_folium(results_map, height=400, width=700)

            st.subheader("Select an Internship to View Details and Route")
            selected = st.selectbox(
                "Choose an internship",
                [f"{m['company']['title']} at {m['company']['Company Name']}" for m in matches]
            )

            if selected:
                selected_company = next(m['company'] for m in matches 
                    if f"{m['company']['title']} at {m['company']['Company Name']}" == selected)
                
                st.write("#### Company Details")
                st.write(f"Company: {selected_company['Company Name']}")
                st.write(f"Required Skills: {', '.join(selected_company['skills'])}")

                if st.button(f"Open Chat for {selected_company['Company Name']}"):  
                    requirements = selected_company['skills']
                    job_title = selected_company['title']

                    interview_data = {
                        "skills": st.session_state.skills, 
                        "requirements": requirements ,
                        "job title": job_title 
                    }
                    
                    temp_file = "interview_data.json"
                    with open(temp_file, "w") as file:
                        json.dump(interview_data, file)
                        run_chainlit_app()
                        st.success("Launching Chainlit app...")
                        time.sleep(2)
                        chainlit_url = "http://localhost:8000"
                        st.success(" launch success...")
                        webbrowser.open(chainlit_url)
                        st.write(f"Visit the [Chainlit interface]({chainlit_url}).")

                show_route = st.button("Show Route")
                if show_route:
                    st.session_state.route_shown = True
                    try:
                        user_coords = f"{user_loc[0]},{user_loc[1]}"
                        company_coords = f"{selected_company['latitude']},{selected_company['longitude']}"
                        
                        steps = gmaps.directions(
                            user_coords,
                            company_coords,
                            mode="driving",
                            language="en",
                            departure_time=datetime.now()
                        )
                        
                        if steps:
                            route_map = folium.Map(location=user_loc, zoom_start=13)
                            
                            folium.Marker(
                                user_loc,
                                popup="Your Location",
                                icon=folium.Icon(color='green')
                            ).add_to(route_map)
                            
                            folium.Marker(
                                [selected_company['latitude'], selected_company['longitude']],
                                popup=selected_company['title'],
                                icon=folium.Icon(color='blue')
                            ).add_to(route_map)
                            
                            for step in steps[0]['legs'][0]['steps']:
                                polyline_points = step['polyline']['points']
                                decoded_points = polyline.decode(polyline_points)
                                folium.PolyLine(
                                    locations=decoded_points,
                                    color='red',
                                    weight=5,
                                    opacity=0.7
                                ).add_to(route_map)
                            
                           
                            st.session_state.current_route = {
                                'map': route_map,
                                'info': steps[0]['legs'][0],
                                'company': selected_company
                            }
                        else:
                            st.error("Could not find a route to this location.")
                    except Exception as e:
                        st.error(f"Error getting route: {str(e)}")
                        st.session_state.route_shown = False

                
                if st.session_state.route_shown and st.session_state.current_route:
                    route_data = st.session_state.current_route
                    st_folium(route_data['map'], height=400, width=700)
                    route_info = route_data['info']
                    st.write("#### Route Information")
                    st.write(f"Distance: {route_info['distance']['text']}")
                    st.write(f"Estimated Time: {route_info['duration']['text']}")
                    st.success(f"Route to {route_data['company']['title']} at {route_data['company']['Company Name']} displayed!")
                    if st.button("Clear Route"):
                        st.session_state.route_shown = False
                        st.session_state.current_route = None
                        st.experimental_rerun()
        else:
            st.warning("No matching internships found based on your skills and location.")

if __name__ == "__main__":
    main()