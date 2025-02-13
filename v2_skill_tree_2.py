import tkinter as tk
from tkinter import ttk, messagebox
import json
import sqlite3
from tkinter import filedialog
import csv
from datetime import datetime

class SkillTreeApp:

    def __init__(self, root):
        self.root = root
        self.root.title("技能樹管理系統")
        self.root.geometry("1200x800")
        
        # 讀取技能類型
        self.skill_types = self.load_skill_types()
        
        # 建立資料庫連接
        self.init_database()
        
        # 建立主要框架
        self.create_main_frame()
        
        # 更新樹狀圖
        self.refresh_data()

    def load_skill_types(self):
        try:
            with open('skill_type.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            messagebox.showerror("錯誤", "找不到 skill_type.json 檔案")
            return {}

    def init_database(self):
        self.conn = sqlite3.connect('skills.db')
        self.cursor = self.conn.cursor()
        
        # 檢查表格是否存在
        self.cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='persons'
        """)
        
        # 如果表格不存在，則創建
        if not self.cursor.fetchone():
            # 建立人員表格
            self.cursor.execute('''
                CREATE TABLE persons (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE
                )
            ''')
            
            # 建立技能表格
            self.cursor.execute('''
                CREATE TABLE skills (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    person_id INTEGER,
                    category TEXT,
                    name TEXT,
                    experience TEXT,
                    FOREIGN KEY (person_id) REFERENCES persons(id),
                    UNIQUE(person_id, category, name)
                )
            ''')
            
            # 建立技能歷史記錄表格
            self.cursor.execute('''
                CREATE TABLE skill_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    skill_id INTEGER,
                    year TEXT,
                    level INTEGER,
                    approve TEXT,
                    FOREIGN KEY (skill_id) REFERENCES skills(id),
                    UNIQUE(skill_id, year)
                )
            ''')
            
            self.conn.commit()
            print("資料庫表格已創建")
        else:
            print("資料庫表格已存在")



    def refresh_data(self):
        # 更新人員下拉選單
        self.cursor.execute("SELECT name FROM persons")
        persons = [row[0] for row in self.cursor.fetchall()]
        self.person_cb['values'] = persons
        
        # 清空並更新樹狀圖
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # 重新載入資料到樹狀圖
        for person in persons:
            person_id = self.tree.insert('', 'end', text=person)
            
            # 查詢該人員的技能
            self.cursor.execute('''
                SELECT s.category, s.name, s.id, s.experience
                FROM skills s
                JOIN persons p ON s.person_id = p.id
                WHERE p.name = ?
            ''', (person,))
            
            skills = self.cursor.fetchall()
            for category, skill_name, skill_id, experience in skills:
                skill_node = self.tree.insert(person_id, 'end', 
                                            text=f"{category} - {skill_name}",
                                            values=(experience,))
                
                # 查詢技能歷史記錄
                self.cursor.execute('''
                    SELECT year, level, approve
                    FROM skill_history
                    WHERE skill_id = ?
                    ORDER BY year
                ''', (skill_id,))
                
                histories = self.cursor.fetchall()
                for year, level, approve in histories:
                    self.tree.insert(skill_node, 'end', 
                                   text=f"{year} - Level {level}",
                                   values=(f"核准者: {approve if approve else 'N/A'}",))

    def create_main_frame(self):
        # 左側框架 - 樹狀圖
        left_frame = ttk.Frame(self.root)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 樹狀圖
        self.tree = ttk.Treeview(left_frame, columns=('info',))
        self.tree.heading('info', text='詳細資訊')
        self.tree.column('info', width=200)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # 添加樹狀圖選擇事件
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)

        # 右側框架 - 操作區
        right_frame = ttk.Frame(self.root)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=10)
        
        # 新增人員區域
        person_frame = ttk.LabelFrame(right_frame, text="新增人員")
        person_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(person_frame, text="姓名:").pack(side=tk.LEFT, padx=5)
        self.person_name = ttk.Entry(person_frame)
        self.person_name.pack(side=tk.LEFT, padx=5)
        ttk.Button(person_frame, text="新增", command=self.add_person).pack(side=tk.LEFT, padx=5)
        
        # 新增技能區域
        skill_frame = ttk.LabelFrame(right_frame, text="新增技能")
        skill_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(skill_frame, text="選擇人員:").pack(padx=5, pady=2)
        self.person_cb = ttk.Combobox(skill_frame)
        self.person_cb.pack(padx=5, pady=2, fill=tk.X)
        
        ttk.Label(skill_frame, text="技能類別:").pack(padx=5, pady=2)
        self.category_cb = ttk.Combobox(skill_frame, values=list(self.skill_types.keys()))
        self.category_cb.pack(padx=5, pady=2, fill=tk.X)
        
        ttk.Label(skill_frame, text="技能名稱:").pack(padx=5, pady=2)
        self.skill_cb = ttk.Combobox(skill_frame)
        self.category_cb.bind('<<ComboboxSelected>>', self.update_skills_cb)
        self.skill_cb.pack(padx=5, pady=2, fill=tk.X)
        
        ttk.Label(skill_frame, text="經驗描述:").pack(padx=5, pady=2)
        self.experience_text = tk.Text(skill_frame, height=8)
        self.experience_text.pack(padx=5, pady=2, fill=tk.X)
        
        # 在 skill_frame 中添加更新經驗按鈕
        button_frame = ttk.Frame(skill_frame)
        button_frame.pack(pady=5)
        ttk.Button(button_frame, text="新增技能", command=self.add_skill).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="更新經驗描述", command=self.update_experience).pack(side=tk.LEFT, padx=5)


        # 更新技能歷史記錄區域
        history_frame = ttk.LabelFrame(right_frame, text="新增技能歷史記錄")
        history_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(history_frame, text="年度:").pack(padx=5, pady=2)
        self.year_entry = ttk.Entry(history_frame)
        self.year_entry.pack(padx=5, pady=2, fill=tk.X)
        
        ttk.Label(history_frame, text="等級(0-5):").pack(padx=5, pady=2)
        self.level_sb = ttk.Spinbox(history_frame, from_=0, to=5)
        self.level_sb.pack(padx=5, pady=2, fill=tk.X)
        
        ttk.Label(history_frame, text="核准人:").pack(padx=5, pady=2)
        self.approve_entry = ttk.Entry(history_frame)
        self.approve_entry.pack(padx=5, pady=2, fill=tk.X)
        
        # 添加歷史記錄按鈕框架
        history_button_frame = ttk.Frame(history_frame)
        history_button_frame.pack(pady=5)
        ttk.Button(history_button_frame, text="新增記錄", command=self.add_history).pack(side=tk.LEFT, padx=5)
        ttk.Button(history_button_frame, text="更新記錄", command=self.update_history).pack(side=tk.LEFT, padx=5)

        # 匯入匯出按鈕
        import_export_frame = ttk.LabelFrame(right_frame, text="資料匯入匯出")
        import_export_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(import_export_frame, text="匯入JSON", command=self.import_json).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(import_export_frame, text="匯出JSON", command=self.export_json).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(import_export_frame, text="匯入CSV", command=self.import_csv).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(import_export_frame, text="匯出CSV", command=self.export_csv).pack(side=tk.LEFT, padx=5, pady=5)

    def update_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # 更新人員下拉選單
        self.cursor.execute("SELECT name FROM persons")
        persons = [row[0] for row in self.cursor.fetchall()]
        self.person_cb['values'] = persons
        
        # 更新樹狀圖
        for person in persons:
            person_id = self.tree.insert('', 'end', text=person)
            
            # 查詢該人員的技能
            self.cursor.execute('''
                SELECT s.category, s.name, s.id
                FROM skills s
                JOIN persons p ON s.person_id = p.id
                WHERE p.name = ?
            ''', (person,))
            
            skills = self.cursor.fetchall()
            for category, skill_name, skill_id in skills:
                skill_node = self.tree.insert(person_id, 'end', text=f"{category} - {skill_name}")
                
                # 查詢技能歷史記錄
                self.cursor.execute('''
                    SELECT year, level, approve
                    FROM skill_history
                    WHERE skill_id = ?
                    ORDER BY year
                ''', (skill_id,))
                
                histories = self.cursor.fetchall()
                for year, level, approve in histories:
                    self.tree.insert(skill_node, 'end', 
                                   text=f"{year} - Level {level} - Approved by: {approve if approve else 'N/A'}")

    def update_skills_cb(self, event=None):
        category = self.category_cb.get()
        if category in self.skill_types:
            self.skill_cb['values'] = self.skill_types[category]

    def add_person(self):
        name = self.person_name.get().strip()
        if name:
            try:
                self.cursor.execute("INSERT INTO persons (name) VALUES (?)", (name,))
                self.conn.commit()
                self.update_tree()
                self.person_name.delete(0, tk.END)
            except sqlite3.IntegrityError:
                messagebox.showerror("錯誤", "此人員已存在")

    def update_experience(self):
        """更新選定技能的經驗描述"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showerror("錯誤", "請選擇一個技能")
            return
            
        selected_item = selection[0]
        item = self.tree.item(selected_item)
        parent = self.tree.parent(selected_item)
        
        # 判斷選擇的是否為技能項目
        item_text = item['text']
        if ' - Level ' in item_text or not parent:  # 如果是歷史記錄或根節點
            messagebox.showerror("錯誤", "請選擇一個技能項目")
            return
            
        # 獲取人員名稱和技能資訊
        person_name = self.tree.item(parent)['text']
        category, skill_name = item_text.split(' - ')
        new_experience = self.experience_text.get("1.0", tk.END).strip()
        
        try:
            # 更新經驗描述
            self.cursor.execute('''
                UPDATE skills
                SET experience = ?
                WHERE id IN (
                    SELECT s.id
                    FROM skills s
                    JOIN persons p ON s.person_id = p.id
                    WHERE p.name = ? AND s.category = ? AND s.name = ?
                )
            ''', (new_experience, person_name, category, skill_name))
            
            self.conn.commit()
            self.refresh_data()
            
            # 清空輸入
            self.experience_text.delete("1.0", tk.END)
            
            messagebox.showinfo("成功", "經驗描述已更新")
            
        except sqlite3.Error as e:
            messagebox.showerror("錯誤", f"資料庫錯誤: {str(e)}")
            self.conn.rollback()
    
    def add_skill(self):
        person = self.person_cb.get()
        category = self.category_cb.get()
        skill_name = self.skill_cb.get()
        experience = self.experience_text.get("1.0", tk.END).strip()
        
        if not all([person, category, skill_name]):
            messagebox.showerror("錯誤", "請填寫完整資訊")
            return
            
        try:
            self.cursor.execute("SELECT id FROM persons WHERE name = ?", (person,))
            person_id = self.cursor.fetchone()[0]
            
            self.cursor.execute('''
                INSERT INTO skills (person_id, category, name, experience)
                VALUES (?, ?, ?, ?)
            ''', (person_id, category, skill_name, experience))
            
            self.conn.commit()
            self.refresh_data()
            
            # 清空輸入
            self.experience_text.delete("1.0", tk.END)
            self.skill_cb.set('')
            messagebox.showinfo("成功", "技能已新增")
            
        except sqlite3.IntegrityError:
            messagebox.showerror("錯誤", "此技能已存在")
        except sqlite3.Error as e:
            messagebox.showerror("錯誤", f"資料庫錯誤: {str(e)}")
            self.conn.rollback()

    def add_history(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showerror("錯誤", "請選擇一個技能")
            return
            
        selected_item = selection[0]
        item = self.tree.item(selected_item)
        parent = self.tree.parent(selected_item)
        
        # 判斷選擇的是否為技能項目
        item_text = item['text']
        if ' - Level ' in item_text or not parent:  # 如果是歷史記錄或根節點
            messagebox.showerror("錯誤", "請選擇一個技能項目")
            return
            
        # 獲取人員名稱和技能資訊
        person_name = self.tree.item(parent)['text']
        category, skill_name = item_text.split(' - ')
        
        year = self.year_entry.get().strip()
        level = self.level_sb.get().strip()
        approve = self.approve_entry.get().strip()
        
        # 基本驗證
        if not year:
            messagebox.showerror("錯誤", "請輸入年度")
            return
        if not level:
            messagebox.showerror("錯誤", "請輸入等級")
            return
        try:
            level = int(level)
            if not 0 <= level <= 5:
                raise ValueError
        except ValueError:
            messagebox.showerror("錯誤", "等級必須是0-5之間的整數")
            return
            
        try:
            # 獲取技能ID
            self.cursor.execute('''
                SELECT s.id
                FROM skills s
                JOIN persons p ON s.person_id = p.id
                WHERE p.name = ? AND s.category = ? AND s.name = ?
            ''', (person_name, category, skill_name))
            
            result = self.cursor.fetchone()
            if not result:
                messagebox.showerror("錯誤", "找不到對應的技能記錄")
                return
                
            skill_id = result[0]
            
            # 檢查是否已存在該年度的記錄
            self.cursor.execute('''
                SELECT id FROM skill_history
                WHERE skill_id = ? AND year = ?
            ''', (skill_id, year))
            
            existing_record = self.cursor.fetchone()
            if existing_record:
                if messagebox.askyesno("確認", f"已存在 {year} 年度的記錄，是否要更新？"):
                    self.cursor.execute('''
                        UPDATE skill_history
                        SET level = ?, approve = ?
                        WHERE skill_id = ? AND year = ?
                    ''', (level, approve, skill_id, year))
                else:
                    return
            else:
                self.cursor.execute('''
                    INSERT INTO skill_history (skill_id, year, level, approve)
                    VALUES (?, ?, ?, ?)
                ''', (skill_id, year, level, approve))
            
            self.conn.commit()
            self.refresh_data()
            
            # 清空輸入
            self.year_entry.delete(0, tk.END)
            self.level_sb.delete(0, tk.END)
            self.level_sb.insert(0, "0")
            self.approve_entry.delete(0, tk.END)
            
            messagebox.showinfo("成功", "歷史記錄已新增/更新")
            
        except sqlite3.Error as e:
            messagebox.showerror("錯誤", f"資料庫錯誤: {str(e)}")
            self.conn.rollback()

    def on_tree_select(self, event):
        selection = self.tree.selection()
        if not selection:
            return
            
        item = selection[0]
        item_data = self.tree.item(item)
        parent = self.tree.parent(item)
        
        # 清空所有輸入欄位
        self.clear_inputs()
        
        if not parent:  # 根節點（人員）
            self.person_cb.set(item_data['text'])
        else:
            parent_data = self.tree.item(parent)
            if not self.tree.parent(parent):  # 技能節點
                # 設置人員
                self.person_cb.set(parent_data['text'])
                
                # 設置技能資訊
                category, skill_name = item_data['text'].split(' - ')
                self.category_cb.set(category)
                self.update_skills_cb()  # 更新技能下拉選單
                self.skill_cb.set(skill_name)
                
                # 設置經驗描述
                self.experience_text.delete("1.0", tk.END)
                self.experience_text.insert("1.0", item_data['values'][0] if item_data['values'] else "")
            else:  # 歷史記錄節點
                # 設置人員和技能
                grandparent = self.tree.parent(parent)
                self.person_cb.set(self.tree.item(grandparent)['text'])
                
                category, skill_name = self.tree.item(parent)['text'].split(' - ')
                self.category_cb.set(category)
                self.update_skills_cb()
                self.skill_cb.set(skill_name)
                
                # 設置歷史記錄資訊
                year, level = item_data['text'].split(' - Level ')
                self.year_entry.delete(0, tk.END)
                self.year_entry.insert(0, year)
                
                self.level_sb.delete(0, tk.END)
                self.level_sb.insert(0, level)
                
                approve = item_data['values'][0].replace('核准者: ', '') if item_data['values'] else ''
                approve = '' if approve == 'N/A' else approve
                self.approve_entry.delete(0, tk.END)
                self.approve_entry.insert(0, approve)

    def clear_inputs(self):
        """清空所有輸入欄位"""
        self.person_cb.set('')
        self.category_cb.set('')
        self.skill_cb.set('')
        self.experience_text.delete("1.0", tk.END)
        self.year_entry.delete(0, tk.END)
        self.level_sb.delete(0, tk.END)
        self.level_sb.insert(0, "0")
        self.approve_entry.delete(0, tk.END)

    def update_history(self):
        """更新歷史記錄"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showerror("錯誤", "請選擇一個歷史記錄")
            return
            
        selected_item = selection[0]
        item = self.tree.item(selected_item)
        parent = self.tree.parent(selected_item)
        
        # 確認選擇的是歷史記錄項目
        if not parent or not self.tree.parent(parent) or ' - Level ' not in item['text']:
            messagebox.showerror("錯誤", "請選擇一個歷史記錄項目")
            return
            
        # 獲取必要資訊
        skill_parent = self.tree.parent(selected_item)
        person_parent = self.tree.parent(skill_parent)
        person_name = self.tree.item(person_parent)['text']
        category, skill_name = self.tree.item(skill_parent)['text'].split(' - ')
        
        # 獲取新的值
        year = self.year_entry.get().strip()
        level = self.level_sb.get().strip()
        approve = self.approve_entry.get().strip()
        
        # 驗證
        if not all([year, level]):
            messagebox.showerror("錯誤", "請填寫完整資訊")
            return
            
        try:
            level = int(level)
            if not 0 <= level <= 5:
                raise ValueError
        except ValueError:
            messagebox.showerror("錯誤", "等級必須是0-5之間的整數")
            return
            
        try:
            # 獲取技能ID
            self.cursor.execute('''
                SELECT s.id
                FROM skills s
                JOIN persons p ON s.person_id = p.id
                WHERE p.name = ? AND s.category = ? AND s.name = ?
            ''', (person_name, category, skill_name))
            
            skill_id = self.cursor.fetchone()[0]
            
            # 更新歷史記錄
            self.cursor.execute('''
                UPDATE skill_history
                SET level = ?, approve = ?
                WHERE skill_id = ? AND year = ?
            ''', (level, approve, skill_id, year))
            
            self.conn.commit()
            self.refresh_data()
            
            messagebox.showinfo("成功", "歷史記錄已更新")
            
        except sqlite3.Error as e:
            messagebox.showerror("錯誤", f"資料庫錯誤: {str(e)}")
            self.conn.rollback()

    def export_json(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        if not filename:
            return
            
        export_data = {}
        
        self.cursor.execute("SELECT name FROM persons")
        persons = [row[0] for row in self.cursor.fetchall()]
        
        for person in persons:
            person_skills = []
            
            self.cursor.execute('''
                SELECT s.id, s.category, s.name, s.experience
                FROM skills s
                JOIN persons p ON s.person_id = p.id
                WHERE p.name = ?
            ''', (person,))
            
            skills = self.cursor.fetchall()
            for skill_id, category, skill_name, experience in skills:
                skill_data = {
                    "category": category,
                    "name": skill_name,
                    "experience": experience,
                    "history": []
                }
                
                self.cursor.execute('''
                    SELECT year, level, approve
                    FROM skill_history
                    WHERE skill_id = ?
                    ORDER BY year
                ''', (skill_id,))
                
                histories = self.cursor.fetchall()
                for year, level, approve in histories:
                    skill_data["history"].append({
                        "year": year,
                        "level": level,
                        "approve": approve
                    })
                
                person_skills.append(skill_data)
            
            export_data[person] = person_skills
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)

    def import_json(self):
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json")]
        )
        if not filename:
            return
            
        with open(filename, 'r', encoding='utf-8') as f:
            import_data = json.load(f)
            
        for person, skills in import_data.items():
            # 新增或獲取人員ID
            self.cursor.execute('''
                INSERT OR IGNORE INTO persons (name)
                VALUES (?)
            ''', (person,))
            
            self.cursor.execute("SELECT id FROM persons WHERE name = ?", (person,))
            person_id = self.cursor.fetchone()[0]
            
            for skill in skills:
                # 新增或更新技能
                self.cursor.execute('''
                    INSERT OR REPLACE INTO skills (person_id, category, name, experience)
                    VALUES (?, ?, ?, ?)
                ''', (person_id, skill['category'], skill['name'], skill['experience']))
                
                skill_id = self.cursor.lastrowid
                
                # 刪除舊的歷史記錄
                self.cursor.execute("DELETE FROM skill_history WHERE skill_id = ?", (skill_id,))
                
                # 新增歷史記錄
                for history in skill['history']:
                    self.cursor.execute('''
                        INSERT INTO skill_history (skill_id, year, level, approve)
                        VALUES (?, ?, ?, ?)
                    ''', (skill_id, history['year'], history['level'], history['approve']))
        
        self.conn.commit()
        self.update_tree()
                  
    def export_csv(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        if not filename:
            return
            
        with open(filename, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            # 寫入標題行
            writer.writerow(['Person', 'Category', 'Skill', 'Experience', 'Year', 'Level', 'Approve'])
            
            self.cursor.execute("""
                SELECT p.name, s.category, s.name, s.experience, 
                       h.year, h.level, h.approve
                FROM persons p
                JOIN skills s ON p.id = s.person_id
                LEFT JOIN skill_history h ON s.id = h.skill_id
                ORDER BY p.name, s.category, s.name, h.year
            """)
            
            for row in self.cursor.fetchall():
                writer.writerow(row)

    def import_csv(self):
        filename = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv")]
        )
        if not filename:
            return
            
        with open(filename, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            current_person = None
            current_skill = None
            current_skill_id = None
            
            for row in reader:
                # 檢查並添加人員
                if current_person != row['Person']:
                    current_person = row['Person']
                    self.cursor.execute('''
                        INSERT OR IGNORE INTO persons (name)
                        VALUES (?)
                    ''', (current_person,))
                    
                    self.cursor.execute("SELECT id FROM persons WHERE name = ?", (current_person,))
                    person_id = self.cursor.fetchone()[0]
                
                # 檢查並添加技能
                skill_key = (row['Category'], row['Skill'])
                if current_skill != skill_key:
                    current_skill = skill_key
                    self.cursor.execute('''
                        INSERT OR REPLACE INTO skills (person_id, category, name, experience)
                        VALUES (?, ?, ?, ?)
                    ''', (person_id, row['Category'], row['Skill'], row['Experience']))
                    current_skill_id = self.cursor.lastrowid
                
                # 添加歷史記錄
                if row['Year']:  # 只有在有年份資料時才添加歷史記錄
                    self.cursor.execute('''
                        INSERT OR REPLACE INTO skill_history (skill_id, year, level, approve)
                        VALUES (?, ?, ?, ?)
                    ''', (current_skill_id, row['Year'], int(row['Level']), row['Approve']))
            
            self.conn.commit()
            self.update_tree()

    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()

def main():
    root = tk.Tk()
    app = SkillTreeApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()