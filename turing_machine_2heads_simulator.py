# Echipa: Ignat Eduardo, Neagu Marian-Madalin

# functie care returneaza o lista cu elementele corespunzatoare
# fiecarei sectiuni
# functia primeste numele sectiunii asa cum apare in config file si o lista
def get_section(name, list_):
    ok = False
    list_section = []
    for line in list_:
        if line == name + ":":
            ok = True
            continue
        if line == "End":
            ok = False
        if ok:
            list_section.append(line)
    return list_section


# functia returneaza un 5 tuplu in care sunt stocate liste corespunzatoare
# cu valorile fiecarei sectiuni.
# Observatie: nu este 7 tuplu, deoarece am convenit sa stocam 'starea de start',
# 'starea de acceptare' si 'starea de reject' in aceeasi lista
def load_tm(file_name):
    list_ = []
    file = open(file_name)

    for line in file:
        line = line.strip()
        # ignoram simbolurile '#' pentru a pune comentarii cu ajutorul lor
        if len(line) > 0 and line[0] != "#":
            list_.append(line)

    list_states = get_section("States", list_)
    list_input_alphabet = get_section("Input alphabet", list_)
    list_tape_alphabet = get_section("Tape alphabet", list_)
    list_transitions_temp = get_section("Transitions", list_)
    list_start_accept_reject_states = get_section("Start state", list_) + get_section("Accept state", list_) + \
                                      get_section("Reject state", list_)
    # pentru a separa fiecare element din fiecare tranzitie am folosit o variabila temporara
    list_transitions = []
    for elem in list_transitions_temp:
        list_transitions.append(elem.split())

    return list_states, list_input_alphabet, list_tape_alphabet, list_transitions, list_start_accept_reject_states


# functia care valideaza fisierul de config pentru TM
# returneaza True daca este validat si Fals daca nu este acceptat
def validate(states, input_alphabet, tape_alphabet, transitions, start_accept_reject_states):
    # prima conditie este ca fiecare sectiune din fisier sa aibe elemente
    if len(states) < 1 or len(input_alphabet) < 1 or len(tape_alphabet) < 1 or len(transitions) < 1 or len(
            start_accept_reject_states) < 1:
        return False

    # urmatoarele conditii verifica daca:
    # - fiecare tranzitie din sectiunea Transitions are 8 elemente si anume (in ordine):
    #           - starea curenta
    #           - starea urmatoare
    #           - caracterul curent la care este capatul care porneste de la inceputul stringului
    #           - caracterul cu care va fi inlocuit caracterul curent la care este capatul mentionat anterior
    #           - directia in care se va deplasa capatul mentionat anterior
    #           - caracterul curent la care este capatul care porneste de la sfarsitul stringului
    #           - caracterul cu care va fi inlocuit caracterul curent la care este capatul mentionat anterior
    #           - directia in care se va deplasa capatul mentionat anterior
    # - fiecare stare (si cea curenta si urmatoarea) exista in multimea de stari
    # - fiecare caracter apartine alfabetului tape
    # - fiecare directie este valida (poate fi R - pentru dreapta, L - pentru stanga, sau N - pentru a
    # ramane in pozitia curenta)
    for transition in transitions:
        if len(transition) != 8:
            return False
        if transition[0] not in states or transition[1] not in states:
            return False
        if transition[2] not in tape_alphabet or transition[3] not in tape_alphabet or \
                transition[5] not in tape_alphabet or transition[6] not in tape_alphabet:
            return False
        if transition[4] not in ['R', 'L', 'N'] or transition[7] not in ['R', 'L', 'N']:
            return False

    # ultima conditie de validare este ca starile de start, acceptare si reject sa se regaseasca
    # in multimea de stari
    for elem in start_accept_reject_states:
        if elem not in states:
            return False

    return True


# functie care returneaza un int in functie de directia pe
# care trebuie sa o ia capatul
def head_move_direction(x):
    if x == 'R':
        return 1
    if x == 'L':
        return -1
    if x == 'N':
        return 0


# functie care interpreteaza inputul dat
def input_interpretation(input_string):
    character_list = input_string.split()
    for character in character_list:
        # daca exista caractere care nu se regasesc in sectiunea 'Input alphabet'
        # atunci stringul nu este din start valid
        if character not in input_alphabet:
            return "Input string not valid!"

    # in lista de caractere, am convenit sa adaugam caracterul _
    # pentru a gestiona mai bine diferite cazuri in config file
    character_list.insert(0, '_')
    character_list.insert(len(character_list), '_')
    # current_state va primi initial starea de start
    current_state = start_accept_reject_states[0]

    # in acest model de TM cu 2 capete si un tape, un capat va porni
    # de la inceputul stringului primit ca input, iar al doilea capat va porni de la
    # sfarsitul acestui string
    current_head_l_index = 1
    current_head_r_index = len(character_list) - 2

    # cat timp starea curenta nu este nici intr-o stare de acceptare, nici intr-o stare
    # de reject, algoritmul de interpretare a input-ului continua
    while current_state != start_accept_reject_states[1] and current_state != start_accept_reject_states[2]:
        for transition in transitions:
            # luand fiecare tranzitie in parte, se verifica daca starea curenta din tranzitia curenta
            # coincide cu starea curenta la care suntem
            if transition[0] == current_state and transition[2] == character_list[current_head_l_index] and transition[5] == \
                    character_list[current_head_r_index]:
                current_state = transition[1]
                # suprascriere caractere
                character_list[current_head_l_index] = transition[3]
                character_list[current_head_r_index] = transition[6]

                # mutare heads in partea corespunzatoare tranzitiei
                current_head_l_index += head_move_direction(transition[4])
                current_head_r_index += head_move_direction(transition[7])
            # daca intra intr-o stare de acceptare sau reject -> break
            if current_state == start_accept_reject_states[1] or current_state == start_accept_reject_states[2]:
                break

    # daca ultima stare este rejected atunci stringul dat a intrat in starea de reject
    if current_state == start_accept_reject_states[2]:
        return "Input rejected!"
    # daca ultima stare este accepted atunci stringul este acceptat si afiseaza output-ul
    return "Input valid. Output: " + str(character_list[1:-1])


# despachetare tuplu in mai multe liste
states, input_alphabet, tape_alphabet, transitions, start_accept_reject_states = load_tm("ex2_1_exemplu.txt")
# bool in care se verifica daca TM este valid
valid = validate(states, input_alphabet, tape_alphabet, transitions, start_accept_reject_states)

# daca TM este valid, atunci se poate primi input de la user
# altfel nu se poate primi input, iar pe ecran se va afisa mesaj corespunzator
if valid:
    print("Config file is valid!")
    string_input = input("String input (with spaces between): ")
    print(input_interpretation(string_input))
else:
    print("Config file is not valid!")
