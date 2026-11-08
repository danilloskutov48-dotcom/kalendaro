import os, sys, json, shutil, datetime, subprocess, holidays
try:
    from plyer import notification
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "plyer"])
    from plyer import notification
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.animation import Animation
from kivy.uix.image import Image, AsyncImage
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDIconButton, MDButton, MDButtonText
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
from kivymd.uix.selectioncontrol import MDCheckbox

Window.size = (360, 640); Window.clearcolor = (0.96, 0.96, 0.98, 1)

GLOBAL_HOLIDAYS = {
    (1,1):("Новый год","party-popper"),(1,7):("Рождество Христово","church"),(1,14):("Старый Новый год","glass-tulip"),(1,19):("Крещение Господне","water"),
    (2,14):("День святого Валентина","heart"),(2,23):("День защитника Отечества","shield-star"),
    (3,8):("Международный женский день","flower"),(3,20):("День весеннего равноденствия","white-balance-sunny"),
    (4,1):("День смеха","emoticon-happy"),(4,12):("День космонавтики","rocket"),
    (5,1):("Праздник Весны и Труда","flower"),(5,9):("День Победы","medal"),
    (6,1):("День защиты детей","balloon"),(6,12):("День России","flag"),
    (7,8):("День семьи, любви и верности","heart-multiple"),
    (8,22):("День Государственного флага РФ","flag-variant"),
    (9,1):("День знаний","school"),(9,13):("День программиста","laptop"),
    (10,5):("День учителя","book-open-variant"),(10,31):("Хэллоуин","pumpkin"),
    (11,4):("День народного единства","account-group"),
    (12,4):("День информатики","desktop-classic"),(12,12):("День Конституции РФ","book-open-page-variant"),(12,25):("Католическое Рождество","pine-tree"),(12,31):("Новый год","firework"),
}
ISLAMIC_HOLIDAYS = {(3,20):("Ураза-байрам","moon-waning-crescent"),(5,27):("Курбан-байрам","sheep")}

USSR_HOLIDAYS = {
    (1,22):("Кровавое воскресенье","hammer-sickle"),
    (2,23):("День Советской Армии","hammer-sickle"),
    (3,8):("8 Марта (СССР)","hammer-sickle"),
    (4,12):("День космонавтики (СССР)","hammer-sickle"),
    (4,22):("День рождения Ленина","hammer-sickle"),
    (5,1):("1 Мая (СССР)","hammer-sickle"),
    (5,9):("День Победы (СССР)","hammer-sickle"),
    (7,7):("День Конституции СССР (1977)","hammer-sickle"),
    (10,7):("День Конституции СССР (1977)","hammer-sickle"),
    (11,7):("Октябрьская революция","hammer-sickle"),
    (11,8):("День воинской славы (СССР)","hammer-sickle"),
    (12,5):("День Конституции СССР (1936)","hammer-sickle"),
    (12,30):("День образования СССР","hammer-sickle"),
}

class GradientHeader(MDBoxLayout):
    def __init__(self, **kw): super().__init__(**kw); self.bind(pos=self.update_canvas, size=self.update_canvas)
    def update_canvas(self, *a):
        self.canvas.before.clear()
        with self.canvas.before:
            for i in range(int(max(self.width, 1))):
                t = i / max(self.width, 1); Color(0.12+0.42*t, 0.45-0.23*t, 0.92-0.12*t, 1); Rectangle(pos=(self.x+i, self.y), size=(1, self.height))

class CircleButton(Button):
    def __init__(self, bg_color, is_today=False, has_events=False, **kw):
        super().__init__(**kw); self.background_normal=''; self.background_color=[0,0,0,0]; self.bg_color=bg_color; self.is_today=is_today; self.has_events=has_events; self.bind(pos=self.update_canvas, size=self.update_canvas)
    def update_canvas(self, *a):
        self.canvas.before.clear()
        with self.canvas.before:
            d = min(self.width, self.height) - dp(6)
            if d <= 0: return
            x = self.x + (self.width-d)/2; y = self.y + (self.height-d)/2
            Color(*self.bg_color); Ellipse(pos=(x,y), size=(d,d))
            if self.is_today: Color(0.1,0.45,0.92,1); Line(circle=(x+d/2,y+d/2,d/2), width=dp(1.5))
            if self.has_events: Color(1,1,1,1); Ellipse(pos=(x+d/2-dp(2.5),y+dp(4)), size=(dp(5),dp(5)))

class ImageButton(ButtonBehavior, AsyncImage): pass

class HolidayCard(MDCard):
    def __init__(self, name, icon, is_active, toggle_func, is_ussr=False, **kw):
        super().__init__(**kw)
        self.orientation = "horizontal"; self.size_hint_y = None; self.height = dp(50); self.radius = [dp(10)]
        self.md_bg_color = [0.98, 0.98, 1, 1] if is_active else [0.9, 0.9, 0.9, 1]
        self.padding = [dp(10), 0, dp(10), 0]
        color = [0.85, 0.25, 0.25, 1] if is_ussr else [0.1, 0.45, 0.92, 1]
        if not is_active: color = [0.6, 0.6, 0.6, 1]
        self.add_widget(MDIconButton(icon=icon, theme_icon_color="Custom", icon_color=color, size_hint_x=None, width=dp(40)))
        self.add_widget(MDLabel(text=name, theme_text_color="Primary" if is_active else "Hint", size_hint_x=1, bold=is_active))
        cb = MDCheckbox(active=is_active, size_hint=(None, None), size=(dp(40), dp(40)), pos_hint={"center_y": 0.5})
        cb.bind(active=lambda inst, val: toggle_func(name, val, self))
        self.add_widget(cb)

class DayMenu(MDCard):
    def __init__(self, screen, date_obj, **kw):
        super().__init__(**kw); self.screen=screen; self.date_obj=date_obj; self.orientation="vertical"; self.size_hint=(1,None); self.height=dp(460); self.radius=[dp(20),dp(20),0,0]; self.md_bg_color=[1,1,1,1]; self.padding=dp(16); self.spacing=dp(10)
        m = ["","января","февраля","марта","апреля","мая","июня","июля","августа","сентября","октября","ноября","декабря"]
        h = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(40))
        h.add_widget(MDLabel(text=f"{date_obj.day} {m[date_obj.month]} {date_obj.year}", bold=True, font_size="22sp", theme_text_color="Primary"))
        h.add_widget(MDIconButton(icon="close", on_release=lambda *a: self.screen.close_day_menu())); self.add_widget(h)
        sh = screen.ru_holidays.get(date_obj); gh = GLOBAL_HOLIDAYS.get((date_obj.month, date_obj.day)); ih = ISLAMIC_HOLIDAYS.get((date_obj.month, date_obj.day)); uh = USSR_HOLIDAYS.get((date_obj.month, date_obj.day))
        if sh: self.add_widget(MDLabel(text=f"Россия: {sh}", theme_text_color="Error", size_hint_y=None, height=dp(30)))
        if gh and screen.is_holiday_enabled(gh[0]):
            row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(30), spacing=dp(5)); row.add_widget(MDIconButton(icon=gh[1], theme_icon_color="Custom", icon_color=[0.8,0.55,0,1], size_hint_x=None, width=dp(30))); row.add_widget(MDLabel(text=gh[0], theme_text_color="Custom", text_color=[0.8,0.55,0,1])); self.add_widget(row)
        if uh and screen.is_holiday_enabled(uh[0]):
            row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(30), spacing=dp(5)); row.add_widget(MDIconButton(icon=uh[1], theme_icon_color="Custom", icon_color=[0.85,0.25,0.25,1], size_hint_x=None, width=dp(30))); row.add_widget(MDLabel(text=uh[0], theme_text_color="Custom", text_color=[0.85,0.25,0.25,1])); self.add_widget(row)
        if ih and screen.is_holiday_enabled(ih[0]):
            row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(30), spacing=dp(5)); row.add_widget(MDIconButton(icon=ih[1], theme_icon_color="Custom", icon_color=[0.2,0.6,0.2,1], size_hint_x=None, width=dp(30))); row.add_widget(MDLabel(text=ih[0], theme_text_color="Custom", text_color=[0.2,0.6,0.2,1])); self.add_widget(row)
        self.add_widget(MDLabel(text="Мои события:", bold=True, size_hint_y=None, height=dp(30)))
        self.events_box = MDBoxLayout(orientation="vertical", spacing=dp(6), size_hint_y=None); self.events_box.bind(minimum_height=self.events_box.setter("height"))
        s = ScrollView(size_hint_y=None, height=dp(210)); inn = MDBoxLayout(orientation="vertical", size_hint_y=None); inn.bind(minimum_height=inn.setter("height")); inn.add_widget(self.events_box); s.add_widget(inn); self.add_widget(s)
        self.add_widget(MDButton(MDButtonText(text="+ Добавить событие"), style="filled", size_hint=(1,None), height=dp(45), on_release=lambda *a: self.screen.open_add_event_dialog(self.date_obj)))
        self.refresh_events()

    def refresh_events(self):
        self.events_box.clear_widgets(); evs = self.screen.get_events_for(self.date_obj)
        if not evs: self.events_box.add_widget(MDLabel(text="Пока пусто. Добавь событие", theme_text_color="Hint", size_hint_y=None, height=dp(40))); return
        for ev in evs:
            c = MDCard(orientation="horizontal", size_hint_y=None, height=dp(75), padding=[dp(8),dp(8),dp(5),dp(8)], spacing=dp(8), radius=[dp(12)], md_bg_color=[0.94,0.94,0.98,1])
            img_p = ev.get("image")
            if img_p and os.path.exists(img_p): c.add_widget(Image(source=img_p, size_hint=(None,1), width=dp(55)))
            else: c.add_widget(MDIconButton(icon="calendar", size_hint=(None,1), width=dp(55), disabled=True))
            info = MDBoxLayout(orientation="vertical", size_hint_x=1)
            info.add_widget(MDLabel(text=ev["title"], bold=True, size_hint_y=None, height=dp(24), size_hint_x=1, shorten=True))
            if ev.get("desc"): info.add_widget(MDLabel(text=ev["desc"], font_size="12sp", theme_text_color="Secondary", size_hint_y=None, height=dp(20), size_hint_x=1, shorten=True))
            c.add_widget(info)
            c.add_widget(MDIconButton(icon="delete", theme_icon_color="Custom", icon_color=[0.85,0.25,0.25,1], pos_hint={"center_y":0.5}, on_release=lambda inst, eid=ev["id"]: self.screen.delete_event(eid, self)))
            self.events_box.add_widget(c)

class CalendarScreen(MDScreen):
    def __init__(self, **kw):
        super().__init__(**kw); self.today=datetime.date.today(); self.cy=self.today.year; self.cm=self.today.month; self.sd=self.today; self.dm=None; self.ov=None
        self.ru_holidays = holidays.Russia(years=[self.cy])
        self.ud = MDApp.get_running_app().user_data_dir; self.ef = os.path.join(self.ud, "events.json"); self.id = os.path.join(self.ud, "images"); self.hf = os.path.join(self.ud, "hidden_holidays.json")
        if not os.path.exists(self.id): os.makedirs(self.id)
        self.ue = self._load_json(self.ef, [])
        self.hidden_hols = self._load_json(self.hf, [])
        self.settings_dialog = None
        ml = MDBoxLayout(orientation="vertical")
        self.hc = GradientHeader(orientation="vertical", size_hint_y=None, height=dp(200), padding=dp(15), spacing=dp(5))
        nav = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(40))
        nav.add_widget(MDIconButton(icon="chevron-left", theme_icon_color="Custom", icon_color=[1,1,1,1], on_release=self.prev_month))
        self.ml = MDLabel(text="", halign="center", bold=True, font_size="22sp", theme_text_color="Custom", text_color=[1,1,1,1]); nav.add_widget(self.ml)
        nav.add_widget(MDIconButton(icon="chevron-right", theme_icon_color="Custom", icon_color=[1,1,1,1], on_release=self.next_month))
        nav.add_widget(MDIconButton(icon="cog", theme_icon_color="Custom", icon_color=[1,1,1,1], on_release=self.open_settings))
        nav.add_widget(MDIconButton(icon="bell", theme_icon_color="Custom", icon_color=[1,1,1,1], on_release=self.test_notification))
        self.hc.add_widget(nav)
        self.tdn = MDLabel(text="", halign="center", theme_text_color="Custom", text_color=[1,1,1,0.7])
        self.tdl = MDLabel(text="", halign="center", bold=True, font_size="28sp", theme_text_color="Custom", text_color=[1,1,1,1])
        self.tyl = MDLabel(text="", halign="center", theme_text_color="Custom", text_color=[1,1,1,0.6])
        self.hc.add_widget(self.tdn); self.hc.add_widget(self.tdl); self.hc.add_widget(self.tyl); ml.add_widget(self.hc)
        gc = MDBoxLayout(orientation="vertical", padding=[dp(16),dp(10),dp(16),0], spacing=dp(5))
        wg = MDGridLayout(cols=7, size_hint_y=None, height=dp(25))
        for n in ["Пн","Вт","Ср","Чт","Пт","Сб","Вс"]:
            cl = [0.85,0.25,0.25,1] if n in ("Сб","Вс") else [0.5,0.5,0.55,1]
            wg.add_widget(MDLabel(text=n, halign="center", bold=True, theme_text_color="Custom", text_color=cl))
        gc.add_widget(wg); self.dg = MDGridLayout(cols=7, spacing=dp(4), size_hint_y=None, height=dp(220)); gc.add_widget(self.dg); ml.add_widget(gc)
        ml.add_widget(MDLabel(text="Нажми на день, чтобы открыть меню", halign="center", theme_text_color="Hint", size_hint_y=None, height=dp(40)))
        self.add_widget(ml); self.render_calendar(); self.update_top_display(self.today)

    def _load_json(self, path, default):
        if not os.path.exists(path): return default
        try:
            with open(path, "r", encoding="utf-8") as f: return json.load(f)
        except: return default

    def _save_json(self, path, data):
        with open(path, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=2)

    def is_holiday_enabled(self, name): return name not in self.hidden_hols

    def open_settings(self, *a):
        box = MDBoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None); box.bind(minimum_height=box.setter("height"))
        box.add_widget(MDLabel(text="Россия и Мир", bold=True, theme_text_color="Primary", size_hint_y=None, height=dp(30)))
        unique_hols = {}
        for k, v in GLOBAL_HOLIDAYS.items(): unique_hols[v[0]] = v[1]
        for k, v in ISLAMIC_HOLIDAYS.items(): unique_hols[v[0]] = v[1]
        for name, icon in sorted(unique_hols.items()):
            box.add_widget(HolidayCard(name, icon, self.is_holiday_enabled(name), self.toggle_holiday))
        box.add_widget(MDLabel(text="Праздники СССР", bold=True, theme_text_color="Error", size_hint_y=None, height=dp(30), padding=[0, dp(10), 0, 0]))
        for name, icon in sorted(USSR_HOLIDAYS.values()):
            box.add_widget(HolidayCard(name, icon, self.is_holiday_enabled(name), self.toggle_holiday, is_ussr=True))
        scroll = ScrollView(size_hint_y=None, height=dp(400)); scroll.add_widget(box)
        self.settings_dialog = MDDialog(MDDialogHeadlineText(text="Настройки праздников"), MDDialogContentContainer(scroll, orientation="vertical"), MDDialogButtonContainer(MDButton(MDButtonText(text="Закрыть"), style="text", on_release=lambda *a: self.settings_dialog.dismiss()), spacing=dp(8)))
        self.settings_dialog.open()

    def toggle_holiday(self, name, is_active, card):
        if is_active and name in self.hidden_hols: self.hidden_hols.remove(name)
        elif not is_active and name not in self.hidden_hols: self.hidden_hols.append(name)
        self._save_json(self.hf, self.hidden_hols)
        card.md_bg_color = [0.98, 0.98, 1, 1] if is_active else [0.9, 0.9, 0.9, 1]
        card.children[2].theme_text_color = "Primary" if is_active else "Hint"
        card.children[2].bold = is_active
        self.render_calendar()

    def test_notification(self, *a):
        try: notification.notify(title="Тест уведомления", message="Всё работает!", app_name="Календарь", timeout=10)
        except Exception as e: print(f"Ошибка: {e}")

    def check_and_send_notifications(self):
        msgs = [f"Событие: {ev['title']}" for ev in self.get_events_for(self.today)]
        gh = GLOBAL_HOLIDAYS.get((self.today.month, self.today.day))
        if gh and self.is_holiday_enabled(gh[0]): msgs.append(f"{gh[0]}")
        uh = USSR_HOLIDAYS.get((self.today.month, self.today.day))
        if uh and self.is_holiday_enabled(uh[0]): msgs.append(f"СССР: {uh[0]}")
        sh = self.ru_holidays.get(self.today)
        if sh: msgs.append(f"Россия: {sh}")
        if msgs:
            msg = "\n".join(msgs)
            try: notification.notify(title="События на сегодня!", message=msg, app_name="Календарь", timeout=10)
            except Exception as e: print(f"Ошибка: {e}")

    def get_events_for(self, d): return [e for e in self.ue if e["date"] == d.isoformat()]
    def has_events(self, d): return bool(self.get_events_for(d))
    def delete_event(self, eid, menu=None):
        self.ue = [e for e in self.ue if e["id"] != eid]; self._save_json(self.ef, self.ue)
        if menu: menu.refresh_events()
        self.render_calendar()

    def open_day_menu(self, d):
        self.sd = d; self.update_top_display(d)
        self.ov = Button(background_color=[0,0,0,0]); self.ov.bind(on_release=lambda *a: self.close_day_menu()); self.add_widget(self.ov)
        Animation(background_color=[0,0,0,0.5], d=0.3).start(self.ov)
        self.dm = DayMenu(self, d, pos_hint={"x":0,"y":0}); self.add_widget(self.dm)
        self.dm.y = -self.dm.height; Animation(y=0, d=0.35, t="out_back").start(self.dm)

    def close_day_menu(self):
        if self.dm:
            anim_ov = Animation(background_color=[0,0,0,0], d=0.2); anim_ov.bind(on_complete=lambda *a: self.remove_widget(self.ov) if self.ov else None); anim_ov.start(self.ov)
            anim_menu = Animation(y=-self.dm.height, d=0.25, t="in_back"); anim_menu.bind(on_complete=lambda *a: self._remove_menu()); anim_menu.start(self.dm)

    def _remove_menu(self):
        if self.dm: self.remove_widget(self.dm); self.dm = None

    def open_add_event_dialog(self, d):
        self.sel_img = None
        self.ti = TextInput(hint_text="Название", multiline=False, size_hint_y=None, height=dp(45))
        self.di = TextInput(hint_text="Описание", multiline=False, size_hint_y=None, height=dp(45))
        self.ib = MDButton(MDButtonText(text="Галерея"), style="tonal", size_hint=(1,None), height=dp(40), on_release=lambda *a: self.open_gallery())
        c = MDBoxLayout(orientation="vertical", spacing=dp(10), size_hint_y=None, height=dp(150)); c.add_widget(self.ti); c.add_widget(self.di); c.add_widget(self.ib)
        self.dlg = MDDialog(MDDialogHeadlineText(text=f"Событие на {d.strftime('%d.%m.%Y')}"), MDDialogContentContainer(c, orientation="vertical"), MDDialogButtonContainer(MDButton(MDButtonText(text="Отмена"), style="text", on_release=lambda *a: self.dlg.dismiss()), MDButton(MDButtonText(text="Сохранить"), style="filled", on_release=lambda *a: self.save_event(d)), spacing=dp(8)))
        self.dlg.open()

    def get_phone_images(self):
        imgs = []; bds = []
        if os.path.exists("/storage/emulated/0"): bds.extend(["/storage/emulated/0/DCIM/Camera", "/storage/emulated/0/Pictures", "/storage/emulated/0/Download"])
        h = os.path.expanduser("~")
        for f in ["Pictures","Downloads","Desktop"]: bds.append(os.path.join(h,f))
        for b in bds:
            if os.path.exists(b):
                try:
                    for r, ds, fs in os.walk(b):
                        if r.count(os.sep) - b.count(os.sep) > 2: del ds[:]; continue
                        for f in fs:
                            if f.lower().endswith(('.png','.jpg','.jpeg')): imgs.append(os.path.join(r,f))
                except: pass
        return imgs

    def open_gallery(self):
        imgs = self.get_phone_images(); l = BoxLayout(orientation='vertical', padding=dp(5), spacing=dp(5))
        if not imgs: l.add_widget(MDLabel(text="Нет картинок", halign="center"))
        else:
            s = ScrollView(); g = MDGridLayout(cols=3, spacing=dp(4), size_hint_y=None); g.bind(minimum_height=g.setter('height'))
            for ip in imgs:
                btn = ImageButton(source=ip, size_hint_y=None, height=dp(100), allow_stretch=True, keep_ratio=False)
                btn.bind(on_release=lambda inst, p=ip: self.sel_img_gallery(p, p_pop))
                g.add_widget(btn)
            s.add_widget(g); l.add_widget(s)
        bc = Button(text="Отмена", size_hint_y=None, height=dp(40)); l.add_widget(bc)
        p_pop = Popup(title="Галерея", content=l, size_hint=(0.95,0.95)); bc.bind(on_release=lambda x: p_pop.dismiss()); p_pop.open()

    def sel_img_gallery(self, path, popup):
        self.sel_img = path; self.ib.children[0].text = "Выбрано"; popup.dismiss()

    def save_event(self, d):
        t = self.ti.text.strip(); ds = self.di.text.strip()
        if not t: return
        fip = None
        if hasattr(self, 'sel_img') and self.sel_img:
            try:
                fn = f"{datetime.datetime.now().timestamp()}_{os.path.basename(self.sel_img)}"; dpth = os.path.join(self.id, fn); shutil.copy(self.sel_img, dpth); fip = dpth
            except Exception as e: print(e)
        self.ue.append({"id": str(datetime.datetime.now().timestamp()), "date": d.isoformat(), "title": t, "desc": ds, "image": fip})
        self._save_json(self.ef, self.ue); self.dlg.dismiss()
        if self.dm: self.dm.refresh_events()
        self.render_calendar(); self.update_top_display(d)

    def render_calendar(self):
        self.dg.clear_widgets()
        m = ["","Январь","Февраль","Март","Апрель","Май","Июнь","Июль","Август","Сентябрь","Октябрь","Ноябрь","Декабрь"]
        self.ml.text = f"{m[self.cm]} {self.cy}"
        fd = datetime.date(self.cy, self.cm, 1); sdw = fd.weekday()
        pm = 12 if self.cm == 1 else self.cm - 1; py = self.cy - 1 if self.cm == 1 else self.cy; dp_ = (fd - datetime.date(py, pm, 1)).days
        nmd = datetime.date(self.cy + 1, 1, 1) if self.cm == 12 else datetime.date(self.cy, self.cm + 1, 1); td = (nmd - fd).days
        for i in range(sdw):
            dn = dp_ - sdw + i + 1; self.dg.add_widget(CircleButton(text=str(dn), bg_color=[0,0,0,0], color=[0.75,0.75,0.8,0.4], disabled=True))
        for day in range(1, td + 1):
            dobj = datetime.date(self.cy, self.cm, day); ist = dobj in self.ru_holidays; isg = (self.cm, day) in GLOBAL_HOLIDAYS and self.is_holiday_enabled(GLOBAL_HOLIDAYS[(self.cm, day)][0]); isi = (self.cm, day) in ISLAMIC_HOLIDAYS and self.is_holiday_enabled(ISLAMIC_HOLIDAYS[(self.cm, day)][0]); isu = (self.cm, day) in USSR_HOLIDAYS and self.is_holiday_enabled(USSR_HOLIDAYS[(self.cm, day)][0]); itod = dobj == self.today; hev = self.has_events(dobj)
            if ist: bg, tc = [0.85,0.25,0.25,1], [1,1,1,1]
            elif isu: bg, tc = [0.85,0.25,0.25,0.15], [0.7,0.1,0.1,1]
            elif isi: bg, tc = [0.2,0.6,0.2,0.3], [0.1,0.4,0.1,1]
            elif isg: bg, tc = [1,0.75,0.14,0.3], [0.7,0.5,0,1]
            elif itod: bg, tc = [0.1,0.45,0.92,0.12], [0.1,0.45,0.92,1]
            else: bg, tc = [0.94,0.94,0.96,1], [0.15,0.15,0.2,1]
            b = CircleButton(text=str(day), bg_color=bg, is_today=itod, has_events=hev, color=tc, bold=itod or ist or isg or isi or isu)
            b.bind(on_release=lambda inst, d=day: self.open_day_menu(datetime.date(self.cy, self.cm, d)))
            b.opacity = 0; Animation(opacity=1, d=0.2, t="out_quad").start(b)
            self.dg.add_widget(b)
        tw = sdw + td; ndn = 1
        while tw < 42:
            self.dg.add_widget(CircleButton(text=str(ndn), bg_color=[0,0,0,0], color=[0.75,0.75,0.8,0.4], disabled=True)); ndn += 1; tw += 1

    def update_top_display(self, d):
        dw = ["Понедельник","Вторник","Среда","Четверг","Пятница","Суббота","Воскресенье"]; mn = ["","января","февраля","марта","апреля","мая","июня","июля","августа","сентября","октября","ноября","декабря"]
        self.tdn.text = dw[d.weekday()]; self.tdl.text = f"{d.day} {mn[d.month]}"; self.tyl.text = str(d.year)

    def prev_month(self, *a):
        self.cm -= 1
        if self.cm < 1: self.cm = 12; self.cy -= 1
        self.ru_holidays = holidays.Russia(years=[self.cy]); self.render_calendar()

    def next_month(self, *a):
        self.cm += 1
        if self.cm > 12: self.cm = 1; self.cy += 1
        self.ru_holidays = holidays.Russia(years=[self.cy]); self.render_calendar()

class MainApp(MDApp):
    def build(self): self.theme_cls.theme_style = "Light"; self.scr = CalendarScreen(); return self.scr
    def on_start(self):
        try:
            from android.permissions import request_permissions, Permission; request_permissions([Permission.POST_NOTIFICATIONS])
        except ImportError: pass
        self.scr.check_and_send_notifications()

if __name__ == "__main__": MainApp().run()