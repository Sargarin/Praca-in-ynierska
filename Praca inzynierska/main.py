from projekt.tts import synthesize_text_with_audio_profile
from projekt.stts import listen_for_speech, stt_google_wav
from deeppavlov import configs, build_model
import os
import stringdist
import re
import googlemaps
from datetime import datetime

# global variable
points = 0
points_MAX = 77


# Metoda łącząca klucz google api podany w pliku z aplikacją
def explicit():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "key.json"


# Metoda sprawdzajaca połączenie z google api
def implicit():
    from google.cloud import storage
    storage_client = storage.Client()
    buckets = list(storage_client.list_buckets())
    print(buckets)


# Metoda obsługująca tekst wypowiedzieny porównująca jego ELEMENTY do porządanych słów kluczowych
def parse_text_without_points(input_text, list_of_words, desirable_dist):
    input_text = input_text.strip().lower()
    print(input_text)
    list_input = list(input_text.split(" "))
    print(list_input)
    for i in list_input:
        value_of_dist = [stringdist.levenshtein(i, word) for word in list_of_words]
        print(value_of_dist)
        min_dist = min(value_of_dist)
        if min_dist < desirable_dist:
            break
    print(min_dist)
    print(list_of_words[value_of_dist.index(min_dist)])
    if min_dist <= 1:
        return True, list_of_words[value_of_dist.index(min_dist)]
    else:
        return False, list_of_words[value_of_dist.index(min_dist)]


# Metoda obsługująca tekst wypowiedzieny porównująca jego TREŚĆ do porządanych słów kluczowych
def parse_phrase(input_text, list_of_words, desirable_dist):
    input_text = input_text.strip().lower()
    print(input_text)
    value_of_dist = [stringdist.levenshtein(input_text, word) for word in list_of_words]
    print(value_of_dist)
    min_dist = min(value_of_dist)
    print(min_dist)
    print(list_of_words[value_of_dist.index(min_dist)])
    if min_dist <= desirable_dist:
        return True, list_of_words[value_of_dist.index(min_dist)]
    else:
        return False, list_of_words[value_of_dist.index(min_dist)]


# Metoda obsługująca tekst wypowiedzieny porównująca jego elementy do porządanych słów kluczowych zliczając
# oraz zwracając ilość dopasowań
def parse_text_with_points(input_text, list_of_words, desirable_dist):
    global value_of_dist, min_dist
    correct_answers = 0
    input_text = input_text.strip().lower()
    print(input_text)
    list_input = list(input_text.split(" "))
    print(list_input)
    for i in list_input:
        value_of_dist = [stringdist.levenshtein(i, word) for word in list_of_words]
        print(value_of_dist)
        min_dist = min(value_of_dist)
        if min_dist < desirable_dist:
            correct_answers += 1
        print(correct_answers)
    print(list_of_words[value_of_dist.index(min_dist)])
    return True, correct_answers


# Metoda zapisująca dane aplikanta do pliku
def save_data(name, birthday, street, city, phone_number, e_mail, experience, experience_where,
              experience_time, management_methods, team_crisis, reaction_to_changes, environment_preference,
              job_change_reason, cons_of_last_job, future_preference, strengths_and_weaknesses, education,
              education_college, data_rozmowy, hobby):
    global points
    mark = (points / points_MAX) * 100
    file = open('data.dat', 'w+')
    file.writelines("Wynik aplikanta :" + str(mark) + " %" +
                    "\nImie i nazwisko Apliaknta : " + name +
                    "\nData urodzenia: " + birthday[0] + " " + birthday[1] + " " + birthday[2] +
                    "\nAdres zamieszkania : " + city + " ul. " + street +
                    "\nNumer Telefonu: " + str(phone_number) +
                    "\nAdres E-mail: " + str(e_mail) +
                    "\nCzy aplikant posiada doświadczenie w zawodzie: " + str(experience) +
                    "\nGdzie nabył doświadczenie: " + str(experience_where) +
                    "\nStaż aplikanta: " + str(experience_time) +
                    "\nZnane aplikantowi metody zarządzania: " + management_methods +
                    "\nCzy aplikant radzi sobie z kryzysami w drużynie: " + team_crisis +
                    "\nJak aplikant reaguje na zmiany: " + reaction_to_changes +
                    "\nPreferencje środowiska: " + environment_preference +
                    "\nPowód zmiany pracy: " + job_change_reason +
                    "\nMinusy poprzedniej pracy: " + cons_of_last_job +
                    "\nGdzie aplikant widzi siebie za 5lat: " + future_preference +
                    "\nMocne i Słabe strony aplikanta " + strengths_and_weaknesses +
                    "\nPoziom wykształcenia aplikanta: " + education +
                    "\nUczelnia ukończona przez aplikanta: " + education_college +
                    "\nHobby aplikanta:" + hobby +
                    "\nData przeprowadzenia rozmowy: " + data_rozmowy)
    file.close()


# Metoda startowa zapisująca i obsługujaca treść wypowiedzi
def get_info():
    text_start = 'Proszę powiedzieć swoje imię i nazwisko.'
    flag_finish = False
    while not flag_finish:
        synthesize_text_with_audio_profile(text_start)
        listen_for_speech(10)
        result = stt_google_wav('output.wav')  # translate audio file
        text, flag_finish, flag_stage = main(result)
        print(text, flag_finish, flag_stage)
        if flag_stage is False:
            count = 0
            while count <= 2:
                synthesize_text_with_audio_profile(text)
                listen_for_speech(10)
                result = stt_google_wav('output.wav')
                count += 1
                text, flag_finish, flag_stage = main(result)
                if flag_stage:
                    break
        text_start = text
    synthesize_text_with_audio_profile(text_start)


# Metoda wychwytujaca i obsługująca parametry zaawansowane
def get_event(input_text, interesting_list_word):
    deep_pavlov_prepro = ner_model([input_text])
    print(deep_pavlov_prepro)
    list_words = deep_pavlov_prepro[0][0]
    list_predict = deep_pavlov_prepro[1][0]
    list_word_predict = list(zip(list_words, list_predict))
    list_name = [i for i, k in list_word_predict if k in interesting_list_word]
    if len(list_name) > 0:
        status = True
    else:
        status = False
    return status, list_name


# Metoda wychwytująca i sprawdzająca poprawność podanej daty urodzenia
def get_birthday(input_text, birth):
    return get_event(input_text, birth)


# Metoda wychwytująca imie i nazwisko aplikanta
def get_name(input_text, name):
    return get_event(input_text, name)


# Metoda pobierająca date przeprowadzenia rozmowy
def get_current_date():
    now = datetime.now()
    today = now.strftime("%m/%d/%Y, %H:%M:%S")
    return today


# Metoda korzystająca z google api wychwytująca adres zamieszkania aplikanta
def get_address(input_text, GEO_LIST):
    stat, addres = get_event(input_text, GEO_LIST)
    if stat:
        addres = ' '.join(addres)
        gmaps = googlemaps.Client(key="AIzaSyBka4wK2D2b_N7hIVmQ-ndX2eV_WtICK1Q")
        final = {}
        geocode_result = gmaps.geocode(input_text)
        data = geocode_result[0]
        for item in data["address_components"]:
            for category in item["types"]:
                data[category] = {}
                data[category] = item["long_name"]
        final["street"] = data.get("route", None)
        final["city"] = data.get("locality", None)
        if final["city"] is not None and final["street"] is not None:
            return True, {"street": final["street"], "city": final["city"]}
        else:
            return False, None
    else:
        return False, None


# Sprawdzenie Regex podanego numeru telefonu
def check_phone_number(phone_number):
    if re.match('[0-9]{9}$', phone_number):
        return True
    else:
        return False


# Metoda wychwyująca i sprawdzająca podany numer telefeonu
def get_phone_number(phone_number):
    type(phone_number)
    print(phone_number)
    phone_number = phone_number.replace(" ", "")
    if check_phone_number(phone_number):
        type(phone_number)
        return True, phone_number
    else:
        return False, phone_number


# Metoda uściślająca podany adres e-mail sprawdzająca jego poprawność Regex-em
# problematyczna,przekręcająca krótkie adresy, z powodu kłopotów ze zrozumiem krótkich fraz przez program
def check_email(email):
    email = email.replace("małpa", "@")
    email = email.replace("kropka", ".")
    email = email.replace(" ", "")

    regex = "(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    if re.search(regex, email):
        print("Valid Email")
        return True, email
    else:
        print("Invalid Email")
        return False, email


# Metyoda wychwytująca i sprawdzająca adres e-mail
def get_e_mail(email):
    print(email)
    email = email.strip()
    stat, email = check_email(email)
    if stat:
        return True, email
    else:
        return False, email


# Metoda wychwytująca odpowiedz aplikanta czy posiada doświadczenie /Max points 5
def get_experience(input_text, yes_no):
    global points
    stat, answer = parse_text_without_points(input_text, yes_no, 1)
    if stat == True and answer == "tak":
        points = points + 5
        return True, input_text
    elif stat == True and answer == "nie":
        return True, input_text
    else:
        return False, input_text


# Metoda wychwytująca miejsce zdobycia przez aplikanta doświadczenia /Max points 8
def get_experience_where(input_text, work_places):
    stat, answer = parse_text_without_points(input_text, work_places, 3)
    global points
    if stat and answer == "nigdzie":
        return True, input_text
    elif stat and answer == "innej":
        return True, input_text
    elif stat:
        points += 8
        return True, input_text
    else:
        return False, input_text


# Metoda wychwytująca długość doświadczenia aplikanta /Max points 9
def get_experience_time(input_text, exp_time):
    stat, answer = parse_text_without_points(input_text, exp_time, 1)
    global points
    if answer == 'zero':
        return True, input_text
    elif answer == 'pół':
        points += 1
        return True, input_text
    elif answer == 'rok':
        points += 2
        return True, input_text
    elif answer == 'dwa':
        points += 4
        return True, input_text
    elif answer == 'trzy':
        points += 6
        return True, input_text
    elif answer == 'cztery':
        points += 8
        return True, input_text
    elif answer == 'ponad':
        points += 9
        return True, input_text
    else:
        return False


# Metoda wychwytująca wszystkie wymienione przez aplikanta metody zarządzania /Max points 8
def get_management_methods(input_text, management_methods_list):
    global points
    if input_text == "nie znam żadnych":
        return True, input_text
    elif input_text != "":
        stat, correct_answers = parse_text_with_points(input_text, management_methods_list, 2)
        points += correct_answers
        return True, input_text
    else:
        return False


# Metoda wychwytujaca słowa klucze dotyczące radzenia sobie z kryzysowymi sytuacjami /Max points 6
def get_team_crisis(input_text, answer_list):
    global points
    stat, answer = parse_text_without_points(input_text, answer_list, 1)
    if stat == True and answer == "nie":
        return True, input_text
    elif stat == True and answer == "tak":
        points += 6
        return True, input_text
    elif stat == True and answer == "różnie":
        points += 3
        return True, input_text
    else:
        return False, input_text


# Metoda wychwytujaca słowa klucze dotyczące reakcji aplikanta na zmiany nastepujące w pracy /Max points 6
def get_reaction_to_changes(input_text, answer_list):
    global points
    stat, answer = parse_text_without_points(input_text, answer_list, 3)
    if stat == True and answer == "negatywnie":
        return True, input_text
    elif stat == True and answer == "pozytywnie":
        points += 6
        return True, input_text
    elif stat == True and answer == "neutralnie":
        points += 3
        return True, input_text
    else:
        return False, input_text


# Metoda wychwytujaca słowa klucze dotyczące preferencji środowiska pracy /Max points 5
def get_environment_preference(input_text, answer_list):
    global points
    stat, answer = parse_text_without_points(input_text, answer_list, 4)
    if stat == True and answer == "spokojne":
        points += 2
        return True, input_text
    elif stat == True and answer == "energiczne":
        points += 5
        return True, input_text
    else:
        return False, input_text


# Metoda wychwytujaca frazy klucze dotyczące powodu zmiany przez aplikanta pracy /Max points 8
def get_job_change_reason(input_text, answer_list):
    global points
    stat, answer = parse_phrase(input_text, answer_list, 7)
    if stat == True and answer == "zbyt niskie zarobki":
        points += 4
        return True, input_text
    elif stat == True and answer == "chęć rozwoju":
        points += 8
        return True, input_text
    elif stat == True and answer == "przeprowadzka":
        points += 6
        return True, input_text
    else:
        return False, input_text


# Metoda wychwytujaca słowa klucze dotyczące wad poprzedniej pracy  /przypuszczam że zawsze występują /Max points 5
def get_cons_of_last_job(input_text):
    global points
    if input_text == "nie było w niej wad":
        points += 2
        return True, input_text
    elif input_text != "":
        points += 5
        return True, input_text
    else:
        return False


# Metoda obsługujaca wypowiedz aplikanta dotyczącą preferencji przyszłosci pracy /Max points 5
def get_future_preference(input_text):
    global points
    if input_text == "nie wiem":
        return True, input_text
    elif input_text != "":
        points += 5
        return True, input_text
    else:
        return False, input_text


# Metoda wychwytujaca słowa klucze dotyczące wad oraz zalet posiadanych przez aplikanta /każdy takowe posiada
# /Max points 5
def get_strengths_and_weaknesses(input_text, answer_lists):
    strengths_list = answer_lists[0]
    weaknesses_list = answer_lists[1]
    global points
    stat_strong, answer_strong = parse_text_with_points(input_text, strengths_list, 3)
    stat_weak, answer_weak = parse_text_with_points(input_text, weaknesses_list, 3)
    sum_of_answers = answer_strong + answer_weak
    if stat_strong == True and stat_weak == True and sum_of_answers > 4:
        points += 5
        return True, input_text
    elif stat_strong == True and stat_weak == True and 2 < sum_of_answers <= 4:
        points += 3
        return True, input_text
    elif stat_strong == True and stat_weak == True and 0 < sum_of_answers <= 2:
        points += 1
        return True, input_text
    else:
        return False, input_text


# Metoda wychwytujaca słowa klucze dotyczące stopnia wykształcenia aplikanta /Max points 5
def get_education(input_text, answer_list):
    global points
    stat, answer = parse_text_without_points(input_text, answer_list, 3)
    if stat == True and answer == "średnie":
        return True, input_text
    elif stat == True and answer == "licencjat":
        points += 2
        return True, input_text
    elif stat == True and answer == "inżynierskie":
        points += 2
        return True, input_text
    elif stat == True and answer == "magisterskie":
        points += 3
        return True, input_text
    elif stat == True and answer == "doktorat":
        points += 4
        return True, input_text
    elif stat == True and answer == "profesure":
        points += 5
        return True, input_text
    else:
        return False, input_text


# Metoda wychwytujaca uczelnie do której uczęszczał aplikant /Max points 1
def get_education_college(input_text):
    global points
    if input_text != "":
        points += 1
        return True, input_text
    else:
        return False, input_text


# Metoda wychwytujaca hobby aplikanta /Max points 1
def get_hobby(input_text):
    global points
    if input_text != "":
        points += 1
        return True, input_text
    else:
        return False, input_text


# Metoda zbierająca wszystkie wypowiedzi aplikanta
def gener_final_text(sumarize_text):
    name = ' '.join(sumarize_text["get_name"])
    birthday = sumarize_text["get_date"]
    address = sumarize_text["get_address"]
    street = address["street"]
    city = address["city"]
    phone_number = sumarize_text["get_phone_number"]
    e_mail = sumarize_text["get_e_mail"]
    experience = sumarize_text["get_experience"]
    experience_where = sumarize_text["get_experience_where"]
    experience_time = sumarize_text["get_experience_time"]
    management_methods = sumarize_text["get_management_methods"]
    team_crisis = sumarize_text["get_team_crisis"]
    reaction_to_changes = sumarize_text["get_reaction_to_changes"]
    environment_preference = sumarize_text["get_environment_preference"]
    job_change_reason = sumarize_text['get_job_change_reason']
    cons_of_last_job = sumarize_text["get_cons_of_last_job"]
    future_preference = sumarize_text["get_future_preference"]
    strengths_and_weaknesses = sumarize_text["get_strengths_and_weaknesses"]
    education = sumarize_text["get_education"]
    education_college = sumarize_text["get_education_college"]
    data_rozmowy = get_current_date()
    hobby = sumarize_text["get_hobby"]
    save_data(name, birthday, street, city, phone_number, e_mail, experience, experience_where,
              experience_time, management_methods, team_crisis, reaction_to_changes, environment_preference,
              job_change_reason, cons_of_last_job, future_preference, strengths_and_weaknesses, education,
              education_college, data_rozmowy, hobby)
    mark = (points / points_MAX) * 100
    mark = str(int(mark))
    return "Dziękuję za Przeprowadzoną rozmowe aplikancie " + name + " . Otrzymałeś wynik " + mark + " %. Miłego dnia"


# Listy parametrów/słów kluczy potrzebnych w metodach

DATE = ['B-DATE', 'I-DATE']
PERSON = ['B-PERSON', 'I-PERSON']
GEO_LIST = ['B-GPE']
WORK_PLACES_LIST = ['nigdzie', 'żabce', 'intelu', 'innej']
IS_EXPERIENCED = ['tak', 'nie']
EXPERIENCE_TIME = ['zero', 'pół ', 'rok', 'półtora', 'dwa', 'trzy ', 'cztery', 'ponad']
MANAGEMENT_METHODS = ['kryzysem', 'decyzyjne', 'zmianą', 'innowacją', 'procesem', 'projektami', 'jakością', 'ryzykiem']
TEAM_CRISIS = ['tak', 'nie', 'różnie']
REACTION_TO_CHANGES = ['pozytywnie', 'negatywnie', 'neutralnie']
ENVIROMENT_PREFERENCE = ['spokojne', 'energiczne']
JOB_CHANGE_REASON = ['zbyt niskie zarobki', 'chęć rozwoju', 'przeprowadzka']
STRENGTHS = ['punktualny', 'pracowity', 'otwarty', 'pomysłowy', 'pomocny', 'energiczny']
WEAKNESSES = ['zamknięty', 'niecierpliwy', 'wybuchowy', 'atencyjny']
EDUCATION = ['średnie', 'licenzjat', 'inżynierskie', 'magisterskie', 'doktorat', 'profesure']

# Słownik statusu etapu rozmowy
status_dict = {"get_name": False,
               "get_date": False,
               "get_address": False,
               "get_phone_number": False,
               "get_e_mail": False,
               "get_experience": False,
               "get_experience_where": False,
               "get_experience_time": False,
               "get_management_methods": False,
               "get_team_crisis": False,
               "get_reaction_to_changes": False,
               "get_environment_preference": False,
               "get_job_change_reason": False,
               "get_cons_of_last_job": False,
               "get_future_preference": False,
               "get_strengths_and_weaknesses": False,
               "get_education": False,
               "get_education_college": False,
               "get_hobby": False}

# Słownik metod przypisanych do etapu rozmowy
dict_functions = {"get_name": get_name,
                  "get_date": get_birthday,
                  "get_address": get_address,
                  "get_phone_number": get_phone_number,
                  "get_e_mail": get_e_mail,
                  "get_experience": get_experience,
                  "get_experience_where": get_experience_where,
                  "get_experience_time": get_experience_time,
                  "get_management_methods": get_management_methods,
                  "get_team_crisis": get_team_crisis,
                  "get_reaction_to_changes": get_reaction_to_changes,
                  "get_environment_preference": get_environment_preference,
                  "get_job_change_reason": get_job_change_reason,
                  "get_cons_of_last_job": get_cons_of_last_job,
                  "get_future_preference": get_future_preference,
                  "get_strengths_and_weaknesses": get_strengths_and_weaknesses,
                  "get_education": get_education,
                  "get_education_college": get_education_college,
                  "get_hobby": get_hobby}

# Słownik wykorzystywanych przez metody parametrów
dict_params = {"get_name": PERSON,
               "get_date": DATE,
               "get_address": GEO_LIST,
               "get_phone_number": None,
               "get_e_mail": None,
               "get_experience": IS_EXPERIENCED,
               "get_experience_where": WORK_PLACES_LIST,
               "get_experience_time": EXPERIENCE_TIME,
               "get_management_methods": MANAGEMENT_METHODS,
               "get_team_crisis": TEAM_CRISIS,
               "get_reaction_to_changes": REACTION_TO_CHANGES,
               "get_environment_preference": ENVIROMENT_PREFERENCE,
               "get_job_change_reason": JOB_CHANGE_REASON,
               "get_cons_of_last_job": None,
               "get_future_preference": None,
               "get_strengths_and_weaknesses": [STRENGTHS, WEAKNESSES],
               "get_education": EDUCATION,
               "get_education_college": None,
               "get_hobby": None}

# Słownik treści pytań przypisanych do etapów rozmowy
quest_stage = {"get_name": "Proszę powiedzieć swoje imię i nazwisko.",
               "get_date": "Proszę podać datę urodzenia. ",
               "get_address": "Proszę podać adres zamieszkania. ",
               "get_phone_number": "Proszę podać numer telefonu.",
               "get_e_mail": "Proszę podać swój adres e-mail",
               "get_experience": "Czy posiadasz doświadczenie w zawodzie menadżera? Jeżeli nie. Należy i tak\
               odpowiedzieć na dwa następne pytania zgodnie z instrukcją",
               "get_experience_where": "Proszę podać nazwę firmy w której nabyłeś doświadczenie jeżeli nie ma jej na \
               liście proszę użyć frazy nabyłem je w innej firmie i podać nazwe firmy",
               "get_experience_time": "Jaki jest twój staż w zawodzie?",
               "get_management_methods": "Jakie znasz metody zarządzania z listy ?",
               "get_team_crisis": "Czy radzisz sobie z kryzysami w zespole?",
               "get_reaction_to_changes": "Jak reagujesz na zmiany następujące w środowisku pracy?",
               "get_environment_preference": "Podaj twoje preferencje pracy,wolisz spokojne czy energiczne środowisko?",
               "get_job_change_reason": "Jaki jest powód chęci zmiany przez ciebie pracy ?",
               "get_cons_of_last_job": "Jakie wady miała twoja poprzednia praca ?",
               "get_future_preference": "Gdzie,odnośnie pracy, widzisz siebie za 5 lat ? ",
               "get_strengths_and_weaknesses": "Wymień proszę, swoje najważniejsze wady i zalety. ",
               "get_education": "Jaki stopień wykształcenia posiadasz ?",
               "get_education_college": "Jaką uczelnie skończyłeś?",
               "get_hobby": "Jakie masz hobby?"}

# Słownik zwróconych przez metody treści odpowiedzi przypisanych do etapu rozmowy
sumarize_text = {"get_name": None,
                 "get_date": None,
                 "get_address": None,
                 "get_phone_number": None,
                 "get_e_mail": None,
                 "get_experience": None,
                 "get_experience_where": None,
                 "get_experience_time": None,
                 "get_management_methods": None,
                 "get_team_crisis": None,
                 "get_reaction_to_changes": None,
                 "get_environment_preference": None,
                 "get_job_change_reason": None,
                 "get_cons_of_last_job": None,
                 "get_future_preference": None,
                 "get_strengths_and_weaknesses": None,
                 "get_education": None,
                 "get_education_college": None,
                 "get_hobby": None}

# Słownik treści powtórzeń pytań w przypadku niezrozumiałej odpowiedzi dla danego etapu rozmowy
quest_repeat = {"get_name": "Nie zrozumiałam prosze powtórzyć imię i nazwisko.",
                "get_date": "Prosze powtórzyć w następujący sposób. szestnastego grudnia 1997 roku.",
                "get_address": "Przepraszam, Proszę powtórzyć adres zamieszkania, miasto oraz ulice.",
                "get_phone_number": "Nie zrozumiałam proszę powtórzyć numer telefonu.",
                "get_e_mail": "Proszę powtórzyć adres email.",
                "get_experience": "Przepraszam , powtórz proszę , czy posiadasz doświadczenie jako menadżer.",
                "get_experience_where": "Prosze powtórzyć nazwe poprzedniej firmy.",
                "get_experience_time": "Przepraszam, proszę powtórzyć długość stażu w przykłądowej postaci zgodnej z \
                listą.",
                "get_management_methods": "Przepraszam, nie zrozumiałam proszę podać znane ci z listy metody \
                zarządzania.",
                "get_team_crisis": "Nie zrozumiałam, prosze powtórzyć, czy radzisz sobie z kryzsami w zespole. ",
                "get_reaction_to_changes": "Przepraszam,jak reagujesz na zmiany  w środowisku pracy.",
                "get_environment_preference": "Nie zrozumiałam, podaj ponownie jakie masz preferencje pracy .",
                "get_job_change_reason": "Przepraszam, powtórz  powód chęci zmiany przez ciebie pracy .",
                "get_cons_of_last_job": "Nie zrozumiałam, powtórz jakie wady miała twoja poprzednia praca .",
                "get_future_preference": "Proszę powtórz, gdzie,odnośnie pracy, widzisz siebie za 5 lat . ",
                "get_strengths_and_weaknesses": "Przepraszam wymień ponownie swoje najważniejsze wady i zalety. ",
                "get_education": "Powtórz Jaki stopień wykształcenia posiadasz .",
                "get_education_college": "Nie zrozumiałam, powtórz ukończoną uczelnie .",
                "get_hobby": "Powtórz proszę swoje hobby"}


# Metoda przedstawiająca bota
def welcome():
    synthesize_text_with_audio_profile(
        'Cześć jestem Patrycja! Jestem tu po to aby wspomóc rekrutera oraz ciebie w weryfikacji twojego CV.')
    synthesize_text_with_audio_profile('Przeprowadzę z toba rozmowe selekcjonującą na stanowisko menadŻera,\
    przypuszczając że aplikujesz do dynamicznie rozwijającej się , nowej firmy, o zwinnym podejściu do pracy ')
    synthesize_text_with_audio_profile('Proszę odpowiadać zgodnie z wytycznymi')


def main(input_text):
    key_list = list(status_dict.keys())
    for i, key in enumerate(key_list):
        key = key
        status_current = status_dict[key]
        if not status_current:
            param = dict_params[key]
            if param is not None:
                status_fun, event = dict_functions[key](input_text, param)
            else:
                status_fun, event = dict_functions[key](input_text)
            if status_fun:
                status_dict[key] = status_fun
                sumarize_text[key] = event
                print(event)
                if i < len(key_list) - 1:
                    return "Dziękuję! " + quest_stage[key_list[i + 1]], False, True
                else:
                    if all(value == True for value in status_dict.values()):
                        return gener_final_text(sumarize_text), True, True
            else:
                return quest_repeat[key], False, False
        else:
            continue


if __name__ == '__main__':
    ner_model = build_model(configs.ner.ner_ontonotes_bert_mult, download=False)
    explicit()
    implicit()
    response = ""
    welcome()
    get_info()
