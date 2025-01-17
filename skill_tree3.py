import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.scrolledtext as scrolledtext
import json
import sqlite3
from datetime import datetime
import xml.etree.ElementTree as ET

class SkillTreeManager:

    def __init__(self, root):
        self.root = root
        self.root.title("技能樹管理系統")
        
        # 載入技能類型定義
        with open('skill_type.json', 'r', encoding='utf-8') as f:
            self.skill_types = json.load(f)
        
        # 建立資料庫連接
        self.conn = sqlite3.connect('skills.db')
        self.create_tables()
        
        self.setup_gui()
        # 載入已存在的資料
        self.load_existing_data()
        
    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS persons (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS skills (
                id INTEGER PRIMARY KEY,
                person_id INTEGER,
                skill_category TEXT,
                skill_name TEXT,
                year_period TEXT,
                skill_level INTEGER,
                experience TEXT,
                FOREIGN KEY (person_id) REFERENCES persons(id)
            )
        ''')
        self.conn.commit()

    def load_existing_data(self):
        cursor = self.conn.cursor()
        
        # 載入所有人員
        cursor.execute("SELECT name FROM persons")
        persons = cursor.fetchall()
        
        # 為每個人建立技能樹
        for person in persons:
            person_name = person[0]
            person_item = self.tree.insert('', 'end', person_name, text=person_name)
            
            # 載入該人員的所有技能
            cursor.execute("""
                SELECT skill_category, skill_name, year_period, skill_level, experience
                FROM skills
                JOIN persons ON skills.person_id = persons.id
                WHERE persons.name = ?
                ORDER BY skill_category, skill_name, year_period
            """, (person_name,))
            
            skills = cursor.fetchall()
            categories = {}
            skill_nodes = {}
            
            for skill in skills:
                category, skill_name, year_period, level, experience = skill
                
                # 建立分類節點
                category_id = f"{person_name}_{category}"
                if category_id not in categories:
                    categories[category_id] = self.tree.insert(person_name, 'end', category_id, text=category)
                
                # 建立技能節點
                skill_id = f"{category_id}_{skill_name}"
                if skill_id not in skill_nodes:
                    skill_nodes[skill_id] = self.tree.insert(category_id, 'end', skill_id, text=skill_name)
                
                # 建立年份和詳細資訊節點
                year_id = f"{skill_id}_{year_period}"
                year_node = self.tree.insert(skill_id, 'end', year_id, text=year_period)
                self.tree.insert(year_id, 'end', f"{year_id}_level", text=f"技能等級: {level}")
                if experience:  # 只有在有經驗描述時才添加節點
                    self.tree.insert(year_id, 'end', f"{year_id}_exp", text=f"技能經驗: {experience}")
        
    def setup_gui(self):
        # 左側面板 - 技能樹顯示
        left_frame = ttk.Frame(self.root)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 技能樹 Treeview
        self.tree = ttk.Treeview(left_frame)
        self.tree.pack(fill=tk.BOTH, expand=True)
        # 綁定選擇事件
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        
        # 右側面板 - 操作區
        right_frame = ttk.Frame(self.root)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=5, pady=5)
        
        # 姓名輸入區
        name_frame = ttk.LabelFrame(right_frame, text="人員資料")
        name_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(name_frame, text="姓名:").pack(side=tk.LEFT, padx=5)
        self.name_entry = ttk.Entry(name_frame)
        self.name_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(name_frame, text="新增人員", command=self.add_person).pack(side=tk.LEFT, padx=5)
        
        # 技能選擇區
        skill_frame = ttk.LabelFrame(right_frame, text="技能資料")
        skill_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(skill_frame, text="技能分類:").pack(fill=tk.X, padx=5)
        self.category_combobox = ttk.Combobox(skill_frame, values=list(self.skill_types.keys()))
        self.category_combobox.pack(fill=tk.X, padx=5)
        self.category_combobox.bind('<<ComboboxSelected>>', self.on_category_selected)
        
        ttk.Label(skill_frame, text="技能名稱:").pack(fill=tk.X, padx=5)
        self.skill_combobox = ttk.Combobox(skill_frame)
        self.skill_combobox.pack(fill=tk.X, padx=5)
        
        # 技能詳細資訊區
        detail_frame = ttk.LabelFrame(right_frame, text="技能詳細資訊")
        detail_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Label(detail_frame, text="年份期間 (例: 2025H1):").pack(fill=tk.X, padx=5)
        self.year_entry = ttk.Entry(detail_frame)
        self.year_entry.pack(fill=tk.X, padx=5)
        
        ttk.Label(detail_frame, text="技能等級 (1-5):").pack(fill=tk.X, padx=5)
        self.level_spinbox = ttk.Spinbox(detail_frame, from_=1, to=5)
        self.level_spinbox.pack(fill=tk.X, padx=5)
        
        ttk.Label(detail_frame, text="技能經驗 (選填):").pack(fill=tk.X, padx=5)
        self.experience_text = scrolledtext.ScrolledText(detail_frame, height=5)
        self.experience_text.pack(fill=tk.BOTH, expand=True, padx=5)
        
        # 按鈕區
        button_frame = ttk.Frame(right_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_frame, text="新增技能", command=self.add_skill).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="儲存", command=self.save_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="匯出MM", command=self.export_mm).pack(side=tk.LEFT, padx=5)

    def on_tree_select(self, event):
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            # 找到選中項目的根節點（人員名稱）
            parent = selected[0]
            while self.tree.parent(parent):
                parent = self.tree.parent(parent)
            
            # 更新姓名輸入框
            person_name = self.tree.item(parent)['text']
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, person_name)
            
    def on_category_selected(self, event):
        category = self.category_combobox.get()
        if category in self.skill_types:
            self.skill_combobox['values'] = self.skill_types[category]
            # 設定技能名稱為第一個選項
            if self.skill_types[category]:
                self.skill_combobox.set(self.skill_types[category][0])
            
    def add_person(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("錯誤", "請輸入姓名")
            return
            
        cursor = self.conn.cursor()
        try:
            cursor.execute("INSERT INTO persons (name) VALUES (?)", (name,))
            self.conn.commit()
            self.tree.insert('', 'end', name, text=name)
            messagebox.showinfo("成功", f"已新增人員: {name}")
        except sqlite3.IntegrityError:
            messagebox.showerror("錯誤", "此姓名已存在")
            
    def add_skill(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("錯誤", "請先選擇人員")
            return
            
        category = self.category_combobox.get()
        skill_name = self.skill_combobox.get()
        year_period = self.year_entry.get()
        skill_level = self.level_spinbox.get()
        experience = self.experience_text.get("1.0", tk.END).strip()
        
        # 修改驗證邏輯，只檢查必填欄位
        if not all([category, skill_name, year_period, skill_level]):
            messagebox.showerror("錯誤", "請填寫必要的技能資訊（技能分類、名稱、年份和等級）")
            return
            
        person_name = self.tree.item(selected[0])['text']
        cursor = self.conn.cursor()
        
        # 取得person_id
        cursor.execute("SELECT id FROM persons WHERE name=?", (person_name,))
        person_id = cursor.fetchone()[0]
        
        # 新增技能資料
        cursor.execute("""
            INSERT INTO skills (person_id, skill_category, skill_name, year_period, skill_level, experience)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (person_id, category, skill_name, year_period, skill_level, experience))
        
        self.conn.commit()
        
        # 更新樹狀圖
        category_id = f"{person_name}_{category}"
        skill_id = f"{category_id}_{skill_name}"
        year_id = f"{skill_id}_{year_period}"
        
        if not self.tree.exists(category_id):
            self.tree.insert(person_name, 'end', category_id, text=category)
        if not self.tree.exists(skill_id):
            self.tree.insert(category_id, 'end', skill_id, text=skill_name)
        if not self.tree.exists(year_id):
            self.tree.insert(skill_id, 'end', year_id, text=year_period)
            self.tree.insert(year_id, 'end', f"{year_id}_level", text=f"技能等級: {skill_level}")
            if experience:  # 只在有填寫經驗時才新增經驗節點
                self.tree.insert(year_id, 'end', f"{year_id}_exp", text=f"技能經驗: {experience}")
            
        messagebox.showinfo("成功", "技能已新增")
        
    def save_data(self):
        self.conn.commit()
        messagebox.showinfo("成功", "資料已儲存")
        
    def export_mm(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("錯誤", "請選擇要匯出的人員")
            return
            
        person_name = self.tree.item(selected[0])['text']
        
        # 建立FreeMind XML結構，設定正確的編碼
        root = ET.Element("map")
        root.set("version", "1.0.1")
        
        # 加入 XML 宣告
        declaration = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>'
        
        # 設定主節點
        main_node = ET.SubElement(root, "node")
        main_node.set("TEXT", person_name)  # 使用 TEXT 屬性而不是 text
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT skill_category, skill_name, year_period, skill_level, experience
            FROM skills
            JOIN persons ON skills.person_id = persons.id
            WHERE persons.name = ?
            ORDER BY skill_category, skill_name, year_period
        """, (person_name,))
        
        skills = cursor.fetchall()
        
        # 建立技能樹結構
        categories = {}
        for skill in skills:
            category, name, year, level, exp = skill
            
            if category not in categories:
                cat_node = ET.SubElement(main_node, "node")
                cat_node.set("TEXT", category)  # 使用 TEXT 屬性
                categories[category] = cat_node
            
            skill_node = ET.SubElement(categories[category], "node")
            skill_node.set("TEXT", name)  # 使用 TEXT 屬性
            
            year_node = ET.SubElement(skill_node, "node")
            year_node.set("TEXT", year)  # 使用 TEXT 屬性
            
            level_node = ET.SubElement(year_node, "node")
            level_node.set("TEXT", f"技能等級: {level}")  # 使用 TEXT 屬性
            
            if exp:  # 只在有經驗描述時才添加節點
                exp_node = ET.SubElement(year_node, "node")
                exp_node.set("TEXT", f"技能經驗: {exp}")  # 使用 TEXT 屬性
        
        # 將 XML 轉換為字串，確保正確的編碼
        xml_str = ET.tostring(root, encoding='unicode')
        
        # 組合完整的 XML 文件
        full_xml = f"{declaration}\n{xml_str}"
        
        # 使用 UTF-8 編碼寫入檔案
        with open(f"{person_name}_skills.mm", 'w', encoding='utf-8') as f:
            f.write(full_xml)

        messagebox.showinfo("成功", f"已匯出到 {person_name}_skills.mm")

    def __del__(self):
        self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = SkillTreeManager(root)
    root.mainloop()