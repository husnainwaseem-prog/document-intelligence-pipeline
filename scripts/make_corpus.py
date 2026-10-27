"""Generate the 24-document corpus: 8 PDF, 8 DOCX, 8 TXT.

Every document is written from the DOCS table below, so the corpus is
fully reproducible: delete corpus/ and re-run this script to rebuild
it byte for byte (modulo PDF metadata timestamps).
"""

from pathlib import Path

import pymupdf
from docx import Document

OUT = Path(__file__).resolve().parents[1] / "corpus"

# (doc_id, title, format, [paragraphs])
DOCS = [
    ("leave_policy", "Employee Leave Policy", "pdf", [
        "Employees receive 25 days of annual leave per year, rising to 28 days after five years of service. Leave must be requested at least two weeks in advance through the HR portal, and managers must approve or reject requests within three working days.",
        "Sick leave is 10 paid days per year. A doctor's note is required for any absence longer than three consecutive days, and unused sick leave does not carry over to the next year.",
        "Maternity leave is 26 weeks at full pay, followed by 13 weeks at statutory pay. Paternity leave is two weeks at full pay, to be taken within eight weeks of the birth.",
        "The notice period for resignation is 30 days. Unused annual leave carries over up to a maximum of 5 days, and any remaining balance is paid out in the final salary.",
    ]),
    ("remote_work", "Remote Work Policy", "pdf", [
        "Employees may work from home up to 3 days per week. Core hours are 10am to 3pm, during which all team members must be online and reachable.",
        "A home office stipend of 200 euros per year is available for equipment such as chairs, monitors, and keyboards. Claims must include a receipt.",
        "All remote work must go through the company VPN, and two-factor authentication is mandatory for every login. Public Wi-Fi must not be used for company systems.",
        "Remote workers must attend the monthly team day in the office. Travel expenses for that day are reimbursed at the standard mileage rate of 0.45 euros per kilometre.",
    ]),
    ("data_privacy", "Data Privacy Policy", "pdf", [
        "Customer data is retained for 90 days after account closure, after which it is permanently deleted from all backups. Marketing data is kept separately and deleted within 30 days of an unsubscribe request.",
        "Any data breach must be reported to the regulator within 72 hours of discovery. The internal incident team must be notified within 4 hours.",
        "Users have the right to request a copy of their personal data, which must be provided within 30 days in a machine-readable format such as CSV.",
        "Passwords must be at least 12 characters long and are stored only as salted hashes. Access to production data requires manager approval and is reviewed every quarter.",
    ]),
    ("solar_system", "The Solar System", "pdf", [
        "Jupiter is the largest planet in the solar system, with a mass greater than all other planets combined. Its Great Red Spot is a storm wider than the Earth.",
        "Saturn's rings are made almost entirely of water ice, and span about 280,000 kilometres across, yet are only about 10 metres thick in places.",
        "Neptune is the farthest planet from the Sun, orbiting at an average distance of 4.5 billion kilometres, and its winds reach 2,100 kilometres per hour.",
        "Mars has the tallest volcano in the solar system, Olympus Mons, which is about 22 kilometres high, nearly three times the height of Mount Everest.",
    ]),
    ("human_heart", "The Human Heart", "pdf", [
        "The human heart beats about 100,000 times per day, pumping roughly 7,500 litres of blood through the body in the same period.",
        "A normal resting heart rate for adults is between 60 and 100 beats per minute. Athletes often have resting rates below 60 beats per minute.",
        "The aorta is the largest artery in the body, carrying oxygen-rich blood from the left ventricle to the rest of the body.",
        "The heart has four chambers: two atria and two ventricles. The left ventricle has the thickest wall because it pumps blood to the whole body.",
    ]),
    ("python_basics", "Python Basics", "pdf", [
        "Python was created by Guido van Rossum and first released in 1991. Its design emphasises readability, using indentation instead of braces to define blocks.",
        "Lists are mutable, meaning their contents can be changed after creation, while tuples are immutable and cannot be changed.",
        "PEP 8 is Python's official style guide. It recommends four spaces per indentation level and a maximum line length of 79 characters.",
        "A dictionary stores key-value pairs and looks up a key in constant time on average. List comprehensions provide a compact way to build lists.",
    ]),
    ("world_war_ii", "The Second World War", "pdf", [
        "The Second World War ended in 1945 with the surrender of Germany in May and Japan in September of that year.",
        "D-Day, the Allied invasion of Normandy, took place on 6 June 1944, involving over 150,000 troops landing on five beaches.",
        "The attack on Pearl Harbor on 7 December 1941 brought the United States into the war the following day.",
        "The Battle of Stalingrad, fought between 1942 and 1943, is considered the turning point of the war on the Eastern Front.",
    ]),
    ("water_cycle", "The Water Cycle", "pdf", [
        "About 97 percent of Earth's water is held in the oceans, while only about 3 percent is freshwater, most of it locked in glaciers and ice caps.",
        "Evaporation turns liquid water into vapour, which rises and cools to form clouds in a process called condensation.",
        "The Amazon River discharges about 209,000 cubic metres of water per second into the Atlantic Ocean, more than the next seven largest rivers combined.",
        "Groundwater makes up about 30 percent of the world's freshwater and supplies drinking water to roughly half the global population.",
    ]),
    ("onboarding_guide", "New Starter Onboarding Guide", "docx", [
        "On your first day, report to reception at 9am with photo identification. Your buddy will meet you there and show you to your desk.",
        "Every new starter is assigned a buddy for the first two weeks. The probation period lasts 3 months, with a review meeting at the halfway point.",
        "IT accounts are created on the morning of your first day. Your laptop is collected from the IT desk on the second floor after the welcome session.",
        "Mandatory training must be completed within the first 30 days, including health and safety, data protection, and anti-harassment modules.",
    ]),
    ("expense_policy", "Expense Policy", "docx", [
        "Meals while travelling are reimbursed up to 25 euros per day. Alcohol is never reimbursable, even when served with a business meal.",
        "Taxi receipts are required for any fare above 15 euros. Rideshare receipts must show the date, route, and total amount.",
        "Expense claims must be submitted within 30 days of the expense. Claims older than 90 days are rejected automatically by the system.",
        "Flights must be booked at least 14 days in advance and in economy class. Business class requires written approval from a director.",
    ]),
    ("french_revolution", "The French Revolution", "docx", [
        "The Bastille prison in Paris was stormed on 14 July 1789, an event now celebrated as France's national day.",
        "The Declaration of the Rights of Man and of the Citizen was adopted in August 1789, proclaiming liberty, property, and equality before the law.",
        "King Louis XVI was executed by guillotine on 21 January 1793, after being found guilty of treason by the National Convention.",
        "The Reign of Terror lasted from 1793 to 1794, during which about 17,000 people were officially executed.",
    ]),
    ("volcanoes", "Volcanoes of the World", "docx", [
        "Mauna Loa in Hawaii is the largest volcano on Earth by volume, rising about 9 kilometres from the ocean floor to its summit.",
        "The 1883 eruption of Krakatoa was heard 3,000 miles away and lowered global temperatures by about 1 degree Celsius for a year.",
        "Mount Vesuvius destroyed Pompeii in 79 AD, burying the city under up to 6 metres of volcanic ash.",
        "The Ring of Fire is a horseshoe-shaped belt around the Pacific Ocean containing about 75 percent of the world's active volcanoes.",
    ]),
    ("shakespeare", "William Shakespeare", "docx", [
        "William Shakespeare wrote 37 plays and 154 sonnets. He was born in Stratford-upon-Avon in 1564.",
        "The Globe Theatre, where many of his plays were first performed, opened in 1599 on the south bank of the River Thames.",
        "Hamlet was first performed around 1603 and contains the famous soliloquy beginning 'To be, or not to be'.",
        "Shakespeare retired to Stratford around 1613 and died on 23 April 1616, at the age of 52.",
    ]),
    ("internet_history", "A Short History of the Internet", "docx", [
        "The first message sent over ARPANET was transmitted in 1969 between UCLA and the Stanford Research Institute.",
        "Tim Berners-Lee proposed the World Wide Web in 1989 while working at CERN, and the first website went live in 1991.",
        "The first email spam was sent in 1978 to about 400 people on ARPANET, advertising a new computer model.",
        "Google was founded in 1998 by Larry Page and Sergey Brin while they were PhD students at Stanford University.",
    ]),
    ("healthy_diet", "Healthy Eating Guide", "docx", [
        "The World Health Organization recommends five portions of fruit and vegetables per day for adults.",
        "Adults should drink about 2 litres of water per day, more in hot weather or during exercise.",
        "Free sugars should make up less than 5 percent of daily energy intake, according to current guidance.",
        "Oily fish such as salmon and mackerel should be eaten at least once a week for omega-3 fatty acids.",
    ]),
    ("electric_vehicles", "Electric Vehicles", "docx", [
        "A typical electric vehicle battery is warranted for 8 years or 160,000 kilometres, whichever comes first.",
        "The Tesla Model 3 became the best-selling electric car in the world in 2020, passing one million units sold in 2021.",
        "Charging an EV at home on a standard wall box takes about 8 hours for a full charge, while a rapid charger can reach 80 percent in about 30 minutes.",
        "Norway leads the world in EV adoption: over 80 percent of new cars sold there in 2022 were fully electric.",
    ]),
    ("moon_landing", "The Moon Landing", "txt", [
        "Apollo 11 landed on the Moon on 20 July 1969. Neil Armstrong was the first person to step onto the lunar surface.",
        "A total of 12 astronauts walked on the Moon across six Apollo missions between 1969 and 1972.",
        "The Apollo 11 command module was named Columbia, and the lunar module was named Eagle.",
        "Buzz Aldrin was the second person to walk on the Moon, following Armstrong down the ladder about 20 minutes later.",
    ]),
    ("amazon_rainforest", "The Amazon Rainforest", "txt", [
        "The Amazon rainforest covers about 5.5 million square kilometres across nine countries in South America.",
        "The Amazon River is about 6,400 kilometres long, making it the second-longest river in the world after the Nile.",
        "About 10 percent of the world's known species live in the Amazon rainforest.",
        "The rainforest produces about 6 percent of the Earth's oxygen through photosynthesis.",
    ]),
    ("chess_rules", "The Rules of Chess", "txt", [
        "Each player starts a game of chess with 16 pieces: one king, one queen, two rooks, two bishops, two knights, and eight pawns.",
        "Castling is the only move that moves two pieces at once, the king and a rook, and it cannot be done if the king is in check.",
        "En passant is a special pawn capture that is only possible immediately after an opponent's pawn moves two squares forward.",
        "Checkmate ends the game at once. A game can also end in stalemate, where the player to move has no legal move but is not in check.",
    ]),
    ("stock_market", "Stock Market Basics", "txt", [
        "A bull market is defined as a rise of 20 percent or more from recent lows, while a bear market is a fall of 20 percent or more.",
        "The New York Stock Exchange was founded in 1792, when 24 brokers signed the Buttonwood Agreement.",
        "Diversification means spreading investments across different assets so that no single failure can wipe out a portfolio.",
        "The first stock exchange in the world was established in Amsterdam in 1602 by the Dutch East India Company.",
    ]),
    ("ancient_egypt", "Ancient Egypt", "txt", [
        "The Great Pyramid of Giza was built around 2560 BC and was the tallest human-made structure for more than 3,800 years.",
        "Egyptian hieroglyphs used about 700 symbols, combining pictures for sounds, words, and ideas.",
        "The annual flooding of the Nile deposited rich silt on farmland, making Egyptian agriculture possible in a desert.",
        "Tutankhamun became pharaoh at about nine years old and ruled for roughly ten years, dying around 1323 BC.",
    ]),
    ("human_brain", "The Human Brain", "txt", [
        "The human brain contains about 86 billion neurons, connected by trillions of synapses.",
        "The brain uses about 20 percent of the body's energy despite making up only about 2 percent of body weight.",
        "The left hemisphere of the brain usually controls language, while the right hemisphere handles spatial attention.",
        "Memories are not stored in one place; recalling an event reactivates a pattern spread across many brain regions.",
    ]),
    ("ocean_depths", "Ocean Depths", "txt", [
        "The Mariana Trench is the deepest place on Earth, reaching a depth of 10,935 metres below sea level.",
        "Sunlight penetrates only the top 200 metres of the ocean, a layer called the epipelagic or sunlight zone.",
        "The pressure at the bottom of the Mariana Trench is over 1,000 times atmospheric pressure at sea level.",
        "Hydrothermal vents on the ocean floor release water heated to over 400 degrees Celsius, yet it does not boil because of the pressure.",
    ]),
    ("wind_energy", "Wind Energy", "txt", [
        "The Betz limit states that no wind turbine can capture more than 59.3 percent of the kinetic energy in wind.",
        "Denmark generated over 40 percent of its electricity from wind in 2022, the highest share of any country.",
        "The largest offshore wind turbines now have rotor diameters over 220 metres, taller than the London Eye.",
        "Wind supplied about 10 percent of global electricity in 2023, up from less than 1 percent in 2000.",
    ]),
    # Distractors: topically close to real documents, but containing none
    # of the evaluation gold phrases. They make retrieval work harder
    # without making any question ambiguous.
    ("leave_around_world", "Paid Leave Around the World", "txt", [
        "Paid vacation varies widely around the world. In many European countries, workers receive between four and six weeks of paid holiday each year.",
        "In the United States, there is no federal minimum for paid vacation, and the typical private-sector worker receives around two weeks.",
        "Some employers offer unlimited vacation policies, though studies suggest employees under such schemes often take fewer days off than those with fixed allowances.",
        "The length of statutory leave is often linked to years of service, and part-time workers usually receive a pro-rated amount.",
    ]),
    ("heart_health", "Keeping Your Heart Healthy", "txt", [
        "Regular exercise strengthens the heart muscle and improves circulation. Doctors recommend at least 150 minutes of moderate activity per week, such as brisk walking or cycling.",
        "A diet low in salt and saturated fat helps keep blood pressure in a healthy range, and eating plenty of vegetables supports heart health.",
        "Smoking is one of the biggest risk factors for heart disease, and quitting improves heart health within weeks.",
        "Stress management, good sleep, and regular check-ups also protect the cardiovascular system over a lifetime.",
    ]),
    ("python_libraries", "Popular Python Libraries", "txt", [
        "Python's ecosystem includes thousands of third-party libraries. NumPy provides fast arrays and numerical routines, while pandas offers dataframes for tabular data.",
        "Requests simplifies HTTP calls, and Flask is a lightweight framework for web applications.",
        "Matplotlib produces charts and plots, and pytest is the standard tool for automated testing.",
        "Most libraries are installed with pip from the Python Package Index, and virtual environments keep project dependencies separate.",
    ]),
    ("war_timeline", "The World Wars in Outline", "txt", [
        "The first half of the twentieth century saw two world wars. The Great War began in 1914 and ended in 1918 with an armistice.",
        "The second global conflict began in 1939 and spread across Europe, Africa, and Asia.",
        "Naval battles in the Pacific and the Eastern Front in Europe were among its largest theatres of operation.",
        "The war reshaped borders, economies, and international institutions for decades afterwards.",
    ]),
    ("planet_exploration", "Exploring the Planets", "txt", [
        "Robotic probes have visited every planet in the solar system. Voyager 1, launched in 1977, is now travelling through interstellar space.",
        "Mars rovers such as Curiosity and Perseverance have searched for signs of ancient water on the red planet.",
        "The Cassini spacecraft spent thirteen years studying Saturn and its moons before its mission ended.",
        "Future missions aim to return samples from Mars and explore the ice-covered oceans of Europa.",
    ]),
    ("ocean_pollution", "Pollution of the Oceans", "txt", [
        "Plastic waste is one of the greatest threats to ocean life. An estimated eight million tonnes of plastic enter the oceans every year.",
        "Coral reefs support about a quarter of marine species despite covering less than one percent of the ocean floor.",
        "Overfishing has reduced many fish stocks, and marine protected areas are one response to the pressure.",
        "Cleaning coastlines and cutting single-use plastics both help reduce the damage to marine ecosystems.",
    ]),
]


def write_pdf(doc_id, title, paragraphs, out_path):
    doc = pymupdf.open()
    for i, para in enumerate(paragraphs):
        page = doc.new_page()
        text = f"{title}\n\n{para}" if i == 0 else para
        page.insert_textbox(pymupdf.Rect(72, 72, 523, 770), text, fontsize=11)
    doc.save(str(out_path))


def write_docx(doc_id, title, paragraphs, out_path):
    doc = Document()
    doc.add_heading(title, level=1)
    for para in paragraphs:
        doc.add_paragraph(para)
    doc.save(str(out_path))


def write_txt(doc_id, title, paragraphs, out_path):
    out_path.write_text(
        title + "\n\n" + "\n\n".join(paragraphs) + "\n", encoding="utf-8"
    )


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for doc_id, title, fmt, paragraphs in DOCS:
        out_path = OUT / f"{doc_id}.{fmt}"
        {"pdf": write_pdf, "docx": write_docx, "txt": write_txt}[fmt](
            doc_id, title, paragraphs, out_path
        )
    from collections import Counter
    counts = Counter(fmt for _, _, fmt, _ in DOCS)
    print(f"Wrote {len(DOCS)} documents: {dict(counts)} -> {OUT}")


if __name__ == "__main__":
    main()
