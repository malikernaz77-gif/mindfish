# mindfish_kivy.py
# Полная версия кода MindFish Deluxe для Kivy (см. предыдущие сообщения)
# --- Вставь сюда весь код из моего прошлого сообщения ---
# mindfish_kivy.py
# MindFish — Kivy версия (single file)
# Требуется: kivy, (опционально) pygame для звуков, но Kivy SoundLoader используется по умолчанию.
from kivy.app import App
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.graphics import Color, Ellipse, Rectangle, RoundedRectangle, Line
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.properties import StringProperty, NumericProperty, ListProperty
import random, math, os, sys, threading

# Настройки окна (для отладки; в APK будет полноэкранный)
Window.size = (500, 850)
Window.clearcolor = (0.04, 0.08, 0.12, 1)

# ---------- Конфиг ----------
AUTO_THRESHOLD = 0.70
TARGET_CHARACTERS = 600
NUM_QUESTIONS = 45
CLICK_SOUND_FILENAME = "click.wav"  # если положишь рядом, будет воспроизводиться

# ---------- Вопросы ----------
QUESTIONS = [
 ("real_person","Это реальный человек?"),
 ("male","Это мужчина?"),
 ("female","Это женщина?"),
 ("young","Персонаж молодой / ребёнок?"),
 ("adult","Персонаж взрослый?"),
 ("fictional","Это вымышленный персонаж?"),
 ("film_tv","Он из фильма или сериала?"),
 ("videogame","Из видеоигр?"),
 ("comics","Из комиксов?"),
 ("anime","Из аниме?"),
 ("cartoon","Мультперсонаж?"),
 ("book","Из книг?"),
 ("superpowers","Есть ли у персонажа сверхспособности?"),
 ("magic","Персонаж использует магию?"),
 ("science","Связан с наукой/технологиями?"),
 ("space","Связан с космосом?"),
 ("weapon","Персонаж использует оружие?"),
 ("mask","Он носит маску?"),
 ("costume","Есть ли у персонажа узнаваемый костюм?"),
 ("hero","Он герой/протагонист?"),
 ("villain","Он злодей/антагонист?"),
 ("detective","Детектив / расследователь?"),
 ("criminal","Преступник?"),
 ("funny","Комедийный / смешной?"),
 ("kids","Известен детям?"),
 ("music","Музыкант / певец?"),
 ("sports","Спортсмен?"),
 ("internet","Интернет-знаменитость / мем?"),
 ("youtuber","Ютубер / стример?"),
 ("franchise_lead","Главный герой крупной франшизы?"),
 ("historical","Историческая личность?"),
 ("politics","Политик?"),
 ("robot","Робот / киборг?"),
 ("animal","Животное / антропоморф?"),
 ("hat","Носит шляпу / кепку?"),
 ("beard","Носит бороду?"),
 ("hotline","Связан с Hotline Miami?"),
 ("dexter","Связан с Dexter (сериал)?"),
 ("ultrakill","Связан с Ultrakill?"),
 ("rickmorty","Связан с Rick and Morty?"),
 ("minecraft","Связан с Minecraft?"),
 ("gamer","Связан с игровой культурой?"),
 ("fringe","Неоднозначный / странный персонаж?"),
 ("historical_famous","Очень известная историческая личность?"),
 ("actor","Актёр?"),
 ("author","Писатель/автор?")
]
NUM_Q = len(QUESTIONS)

# ---------- Персонажи ----------
CHARACTERS = []
def add_char(name, tags, desc=""):
    CHARACTERS.append({'id': len(CHARACTERS), 'name': name, 'tags': set(tags), 'desc': desc or ", ".join(sorted(tags))})

# Несколько ключевых персонажей (курируем вручную)
add_char("Декстер Морган", {"film_tv","dexter","adult","criminal","male","detective"}, "Судмедэксперт и скрывающийся серийный убийца.")
add_char("Декстер (лаборатория)", {"cartoon","young","fictional","science","male"}, "Ребёнок-изобретатель из 'Лаборатории Декстера'.")
add_char("Рик Санчез", {"cartoon","rickmorty","science","franchise_lead","male","internet"}, "Гениальный, но небрежный учёный.")
add_char("Морти Смит", {"cartoon","rickmorty","young","male"}, "Внук Рика, часто в неприятностях.")
add_char("Человек-паук", {"comics","superpowers","mask","hero","franchise_lead","male"}, "Питер Паркер — стреляет паутиной.")
add_char("Питер Паркер", {"comics","superpowers","mask","hero","male"}, "Настоящее имя Человека-паука.")
add_char("Jacket", {"videogame","hotline","weapon","male"}, "Главный персонаж Hotline Miami.")
add_char("Ultrakill Protagonist", {"videogame","ultrakill","weapon","male"}, "Протагонист Ultrakill.")
add_char("Гарри Поттер", {"book","film_tv","magic","franchise_lead","young"}, "Мальчик-волшебник.")
add_char("Шерлок Холмс", {"book","detective","male"}, "Величайший сыщик литературы.")
add_char("Илон Маск", {"real_person","science","internet","male"}, "Предприниматель и инженер.")
add_char("Альберт Эйнштейн", {"real_person","science","historical","male"}, "Физик-теоретик.")
add_char("Наполеон Бонапарт", {"real_person","historical","ruler","male"}, "Французский полководец.")
add_char("Клеопатра", {"real_person","historical","ruler","female"}, "Царица Египта.")
add_char("PewDiePie", {"real_person","youtuber","internet","male","gamer"}, "Популярный видеоблогер.")
add_char("MrBeast", {"real_person","youtuber","internet","male"}, "Известный ютубер.")
add_char("Шрек", {"cartoon","film_tv","funny","male","franchise_lead"}, "Огр — герой мультфильма.")

# Немного известных дополнительно
more = [
 ("Тони Старк", {"comics","science","male"}),
 ("Бэтмен", {"comics","mask","hero","male"}),
 ("Джокер", {"comics","villain","male"}),
 ("Дарт Вейдер", {"film_tv","space","villain","male"}),
 ("Лара Крофт", {"videogame","franchise_lead","female"}),
 ("Гоку", {"anime","superpowers","male"}),
 ("Наруто", {"anime","superpowers","male"}),
 ("Гэндальф", {"book","magic","male"}),
 ("Фродо", {"book","fantasy","male"}),
 ("Мария (актер)", {"real_person","actor"})
]
for n,t in more:
    add_char(n,t)

# Генерация дополнительных персонажей до TARGET_CHARACTERS
FRANCHISE_BASES = [
 "Hotline Miami", "Rick and Morty", "Dexter", "Ultrakill", "Marvel", "DC",
 "Pokemon", "Mario", "Zelda", "Doom", "Halo", "Star Wars", "Lord of the Rings",
 "Minecraft", "Fortnite", "Overwatch"
]
ADDITIONAL_BASE_CHARACTERS = [
 "Jacket", "Beard", "Richter", "Birdperson", "Mr. Meeseeks", "Unity",
 "Debra Morgan", "Harry Morgan", "V1", "V2", "Valkyrie", "Deadpool",
 "Wolverine", "Nathan Drake", "Master Chief", "Aloy", "Kratos"
]

def gen_tags_for_franchise(base):
    tags = set()
    ln = base.lower()
    if "hotline" in ln or base in ("Jacket","Beard","Richter"):
        tags.update({"videogame","hotline","weapon"})
    if "rick" in ln or base in ("Birdperson","Mr. Meeseeks","Unity"):
        tags.update({"cartoon","rickmorty"})
    if "dexter" in ln or base in ("Debra Morgan","Harry Morgan"):
        tags.update({"film_tv","dexter"})
    if "ultrakill" in ln or base in ("V1","V2","Valkyrie"):
        tags.update({"videogame","ultrakill","weapon"})
    if base.lower() in ("deadpool","wolverine"):
        tags.update({"comics","marvel","superpowers"})
    if base.lower() in ("mario","luigi"):
        tags.update({"videogame","franchise_lead"})
    if random.random() < 0.10:
        tags.add("franchise_lead")
    if random.random() < 0.03:
        tags.add("real_person")
    if random.random() < 0.08:
        tags.add("internet")
    return tags

i = len(CHARACTERS)
while i < TARGET_CHARACTERS:
    if random.random() < 0.6:
        base = random.choice(ADDITIONAL_BASE_CHARACTERS + FRANCHISE_BASES)
        name = base if random.random() < 0.6 else f"{base} {random.randint(1,499)}"
        tags = gen_tags_for_franchise(base)
    else:
        prefixes = ["Neo","Shadow","Blade","Nova","Azure","Crimson","Silent","Iron","Silver","Phantom","Prime"]
        suffixes = ["walker","runner","strike","reaper","blade","ghost","rider","hawk","spear"]
        name = random.choice(prefixes) + random.choice(suffixes)
        if random.random() < 0.35:
            name += f" {random.randint(2,499)}"
        tags = set()
        if random.random() < 0.45: tags.add("videogame")
        if random.random() < 0.2: tags.add("comics")
        if random.random() < 0.12: tags.add("anime")
        if random.random() < 0.09: tags.add("internet")
        if random.random() < 0.14: tags.add("hero")
        if random.random() < 0.07: tags.add("villain")
        if random.random() < 0.12: tags.add("weapon")
    desc = []
    if "videogame" in tags: desc.append("из видеоигр")
    if "cartoon" in tags: desc.append("мультперсонаж")
    if "hotline" in tags: desc.append("Hotline Miami")
    if "rickmorty" in tags: desc.append("Rick and Morty")
    if "dexter" in tags: desc.append("Dexter (сериал)")
    if not desc:
        desc = ["персонаж"]
    add_char(name, tags, desc=", ".join(desc))
    i += 1

# Обновим id
for idx,c in enumerate(CHARACTERS):
    c['id'] = idx

# ---------- Базовая инференция (байес) ----------
def compute_posteriors(candidates, answers):
    logs = []
    for c in candidates:
        logp = 0.0
        for qidx, (tag, _) in enumerate(QUESTIONS):
            ans = answers[qidx]
            if ans is None:
                continue
            has = (tag in c['tags'])
            # likelihoods tuned
            if ans == 1:
                p = 0.93 if has else 0.07
            else:
                p = 0.07 if has else 0.93
            p = max(min(p, 0.999999), 1e-9)
            logp += math.log(p)
        logs.append((logp, c))
    if not logs:
        return []
    max_log = max(l for l,_ in logs)
    exps = [(math.exp(l - max_log), c) for l,c in logs]
    s = sum(w for w,_ in exps)
    if s == 0:
        n = len(exps)
        return [(1.0/n, c) for _,c in exps]
    return [(w/s, c) for w,c in exps]

def entropy(dist):
    H = 0.0
    for p,_ in dist:
        if p > 0:
            H -= p * math.log2(p)
    return H

def expected_entropy_if_asked(candidates, answers, qidx):
    dist = compute_posteriors(candidates, answers)
    if not dist: return 0.0
    p_yes = sum(p for p,c in dist if QUESTIONS[qidx][0] in c['tags'])
    p_no = max(0.0, 1.0 - p_yes)
    def posterior_entropy(answer_val):
        arr=[]
        for p,c in dist:
            has = QUESTIONS[qidx][0] in c['tags']
            lik = 0.93 if (answer_val==1 and has) or (answer_val==0 and not has) else 0.07
            arr.append((p*lik, c))
        s = sum(w for w,_ in arr)
        if s == 0: return 0.0
        arr_norm = [(w/s, c) for w,c in arr]
        return entropy(arr_norm)
    H_yes = posterior_entropy(1)
    H_no = posterior_entropy(0)
    return p_yes * H_yes + p_no * H_no

def pick_best_question(candidates, answers, pool_size=30):
    unanswered = [i for i,a in enumerate(answers) if a is None]
    if not unanswered: return None
    dist = compute_posteriors(candidates, answers)
    if not dist:
        return random.choice(unanswered)
    ent_list=[]
    for i in unanswered:
        p_yes = sum(p for p,c in dist if QUESTIONS[i][0] in c['tags'])
        p_no = max(0.0, 1.0 - p_yes)
        def H(p): return -p*math.log2(p) if p>0 else 0
        ent = H(p_yes) + H(p_no)
        ent_list.append((ent,i))
    ent_list.sort(reverse=True)
    pool = [i for _,i in ent_list[:min(len(ent_list), pool_size)]]
    current_entropy = entropy(dist)
    best_q = None; best_gain = -1e9
    for q in pool:
        exp_ent = expected_entropy_if_asked(candidates, answers, q)
        gain = current_entropy - exp_ent
        if gain > best_gain:
            best_gain = gain; best_q = q
    if best_q is None:
        return random.choice(unanswered)
    return best_q

# ---------- Звук ----------
click_sound = None
try:
    if os.path.exists(CLICK_SOUND_FILENAME):
        click_sound = SoundLoader.load(CLICK_SOUND_FILENAME)
except Exception:
    click_sound = None

def play_click():
    if click_sound:
        try:
            click_sound.play()
        except Exception:
            pass

# ---------- UI компоненты ----------

class MindFishCanvas(RelativeLayout):
    """Рисуем и анимируем рыбку-каплю (MindFish) прямо на Canvas."""
    blink = False
    eye_offset = NumericProperty(0)
    mouth_smile = NumericProperty(0.0)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            # фон карточки (полупрозрачный)
            self.bg_color = Color(0.06,0.12,0.18,1)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[12])
        self.bind(pos=self._update_bg, size=self._update_bg)
        # schedule animation
        self._time = 0.0
        Clock.schedule_interval(self._animate, 1/30.)

    def _update_bg(self, *a):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def _animate(self, dt):
        # простая анимация: глаза двигаются и моргание
        self._time += dt
        self.eye_offset = math.sin(self._time*2.0) * 6
        # моргание примерно раз в 3-6 секунд
        if random.random() < 0.02:
            self.blink = True
            Clock.schedule_once(self._end_blink, 0.12)
        # улыбка медленно меняется
        self.mouth_smile = 0.4 + 0.6 * math.sin(self._time*1.1) * 0.2
        self.canvas.ask_update()

    def _end_blink(self, dt):
        self.blink = False

    def on_size(self, *a):
        self.canvas.ask_update()

    def on_pos(self, *a):
        self.canvas.ask_update()

    def on_eye_offset(self, *a):
        self.canvas.ask_update()

    def on_mouth_smile(self, *a):
        self.canvas.ask_update()

    def on_canvas(self, *a):
        pass

    def draw(self):
        # manual drawing each frame to reflect properties
        self.canvas.clear()
        with self.canvas:
            # фон (внутри фрейма)
            Color(0.05,0.13,0.2,1)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[12])
            # fish body (drop shape) centered
            w,h = self.width*0.7, self.height*0.6
            cx = self.x + self.width*0.5
            cy = self.y + self.height*0.55
            # body
            Color(0.2,0.75,0.9,1)
            Ellipse(pos=(cx - w*0.5, cy - h*0.5), size=(w,h))
            # tail (small)
            Color(0.18,0.7,0.85,1)
            Ellipse(pos=(cx + w*0.22, cy - h*0.18), size=(w*0.28,h*0.28))
            # hat
            Color(0.06,0.06,0.06,1)
            hat_w = w*0.5; hat_h = h*0.18
            RoundedRectangle(pos=(cx - hat_w*0.5, cy + h*0.18), size=(hat_w, hat_h), radius=[6])
            Color(0,0,0,1)
            Rectangle(pos=(cx - hat_w*0.6, cy + h*0.12), size=(hat_w*1.2, hat_h*0.3))
            # monocle: on right eye
            eye_y = cy + h*0.06
            eye_x_left = cx - w*0.12
            eye_x_right = cx + w*0.05
            eye_size = min(w,h)*0.12
            # eyes
            Color(1,1,1,1)
            Ellipse(pos=(eye_x_left - eye_size*0.5 + self.eye_offset*0.2, eye_y - eye_size*0.5), size=(eye_size, eye_size))
            Ellipse(pos=(eye_x_right - eye_size*0.5 + self.eye_offset*0.3, eye_y - eye_size*0.5), size=(eye_size, eye_size))
            # pupils
            Color(0,0,0,1)
            pup = eye_size*0.4
            Ellipse(pos=(eye_x_left - pup*0.5 + self.eye_offset*0.5, eye_y - pup*0.5), size=(pup,pup))
            Ellipse(pos=(eye_x_right - pup*0.5 + self.eye_offset*0.5, eye_y - pup*0.5), size=(pup,pup))
            # monocle ring on right eye
            Color(0.9,0.9,0.6,1)
            Line(circle=(eye_x_right, eye_y, eye_size*0.6), width=1.6)
            # chain to hat
            Color(0.9,0.9,0.6,0.6)
            Line(points=[eye_x_right + eye_size*0.4, eye_y - eye_size*0.2, cx + hat_w*0.1, cy + h*0.22], width=1.1)
            # mouth (smile)
            Color(0.06,0.06,0.06,1)
            ms = self.mouth_smile
            Line(points=[cx - w*0.1, cy - h*0.15, cx, cy - h*0.18 - ms*2, cx + w*0.12, cy - h*0.15], width=1.8, cap='round')

    def on_touch_down(self, touch):
        # перерисовать (ощущение интерактивности)
        self.blink = True
        Clock.schedule_once(self._end_blink, 0.12)
        return super().on_touch_down(touch)

    def on_canvas_update(self, *a):
        pass

    def on_parent(self, widget, parent):
        # будем рисовать на каждом кадре
        Clock.schedule_interval(lambda dt: self.draw(), 1/30.)

class CenteredLabel(Label):
    pass

class MindFishUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=10, spacing=8, **kwargs)
        # Header
        self.header = Label(text="Я — MindFish. Отвечай — я попробую угадать.", size_hint=(1, None), height=40, halign='center', valign='middle', bold=True)
        self.header.bind(size=self._update_header_texture)
        self.add_widget(self.header)
        # fish canvas area
        self.fish_area = MindFishCanvas(size_hint=(1, None), height=260)
        self.add_widget(self.fish_area)
        # question area
        self.q_card = BoxLayout(orientation='vertical', size_hint=(1, None), height=160, padding=8)
        self.q_label = Label(text="Нажми любую кнопку чтобы начать", halign='center', valign='middle', font_size='18sp')
        self.q_label.bind(size=self._update_q_label)
        self.q_card.add_widget(self.q_label)
        self.add_widget(self.q_card)
        # buttons row
        btn_row = BoxLayout(orientation='horizontal', size_hint=(1, None), height=80, spacing=8)
        self.btn_yes = Button(text="Да", on_release=lambda x: self.on_answer(1), background_normal='', background_color=(0.12,0.7,0.45,1))
        self.btn_no = Button(text="Нет", on_release=lambda x: self.on_answer(0), background_normal='', background_color=(0.85,0.2,0.2,1))
        self.btn_dk = Button(text="Не знаю", on_release=lambda x: self.on_answer(None), background_normal='', background_color=(0.15,0.45,0.85,1))
        btn_row.add_widget(self.btn_yes)
        btn_row.add_widget(self.btn_no)
        btn_row.add_widget(self.btn_dk)
        self.add_widget(btn_row)
        # bottom controls
        bottom = BoxLayout(orientation='horizontal', size_hint=(1, None), height=60, spacing=8)
        self.btn_guess = Button(text="Угадать", on_release=lambda x: self.make_guess(), background_normal='', background_color=(0.95,0.74,0.24,1))
        self.btn_add = Button(text="Добавить", on_release=lambda x: self.add_character_popup(), background_normal='', background_color=(0.23,0.5,0.95,1))
        self.btn_reset = Button(text="Сброс", on_release=lambda x: self.reset_all(), background_normal='', background_color=(0.45,0.47,0.5,1))
        bottom.add_widget(self.btn_guess)
        bottom.add_widget(self.btn_add)
        bottom.add_widget(self.btn_reset)
        self.add_widget(bottom)
        # status / guess info
        self.guess_label = Label(text="", size_hint=(1, None), height=60, halign='center', valign='middle')
        self.guess_label.bind(size=self._update_guess_texture)
        self.add_widget(self.guess_label)
        # state
        self.answers = [None]*NUM_Q
        self.candidates = CHARACTERS[:]
        self.current_q = None
        self.asked = []
        # start first question after small delay
        Clock.schedule_once(lambda dt: self.next_question(), 0.6)

    def _update_header_texture(self, *a):
        self.header.text_size = self.header.size

    def _update_q_label(self, *a):
        self.q_label.text_size = self.q_label.size

    def _update_guess_texture(self, *a):
        self.guess_label.text_size = self.guess_label.size

    def update_status(self):
        answered = sum(1 for a in self.answers if a is not None)
        self.header.text = f"Отвечено: {answered} • Кандидатов: {len(self.candidates)}"

    def next_question(self):
        q = pick_best_question(self.candidates, self.answers)
        if q is None:
            self.make_guess()
            return
        self.current_q = q
        if q not in self.asked:
            self.asked.append(q)
        self.q_label.text = QUESTIONS[q][1]
        self.update_status()

    def on_answer(self, val):
        # звук
        try:
            threading.Thread(target=play_click, daemon=True).start()
        except:
            pass
        if self.current_q is None:
            self.next_question()
            return
        self.answers[self.current_q] = val
        self.update_status()
        post = compute_posteriors(self.candidates, self.answers)
        if post:
            top_prob, top_c = max(post, key=lambda x: x[0])
            if top_prob >= AUTO_THRESHOLD:
                self.show_guess(top_prob, top_c)
                return
      