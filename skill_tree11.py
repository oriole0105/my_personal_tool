import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import tkinter.scrolledtext as scrolledtext
import json
import sqlite3
from datetime import datetime
import xml.etree.ElementTree as ET

class SkillTreeManager:
    
    #===========================================
    #  Initial 
    #===========================================
    def __init__(self, root):
        self.root = root
        self.root.title("技能樹管理系統 V1.11")

        # 載入技能類型定義
        with open('skill_type.json', 'r', encoding='utf-8') as f:
            self.skill_types = json.load(f)
        
        # 建立資料庫連接
        self.conn = sqlite3.connect('skills.db')
        self.create_tables()
        
        self.setup_gui()
        # 載入已存在的資料
        self.load_existing_data()

        self.selected_item = None  # 追踪當前選中的項目

        # 配置 Treeview 樣式以支援多行文字
        #style = ttk.Style()
        #style.configure('Treeview', rowheight=60)  # 設定預設行高
        #style.configure('Treeview.Heading', font=('TkDefaultFont', 9, 'bold'))  # 設定標題樣式

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
        
            # 載入該人員的所有技能，按照類別、技能名稱排序
            cursor.execute("""
                SELECT skill_category, skill_name, year_period, skill_level, experience
                FROM skills
                JOIN persons ON skills.person_id = persons.id
                WHERE persons.name = ?
                ORDER BY skill_category, skill_name, 
                    CASE 
                        WHEN year_period LIKE '%H2' THEN year_period || '2'
                        WHEN year_period LIKE '%H1' THEN year_period || '1'
                        ELSE year_period
                    END
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

    #===========================================
    #  View 
    #===========================================
    def setup_gui(self):
        # 建立分頁
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 主要操作分頁
        main_frame = ttk.Frame(self.notebook)
        self.notebook.add(main_frame, text='技能管理')
        
        # 查詢分頁
        search_frame = ttk.Frame(self.notebook)
        self.notebook.add(search_frame, text='查詢')
        
        # 主要操作分頁的內容
        # 主選單
        menubar = tk.Menu(self.root, tearoff=0)
        self.root.config(menu=menubar)
        
        # 檔案選單
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="檔案", menu=file_menu)
        file_menu.add_command(label="匯出JSON", command=self.export_json)
        file_menu.add_command(label="匯入JSON", command=self.import_json)
        file_menu.add_separator()
        file_menu.add_command(label="匯出MM", command=self.export_mm)
        file_menu.add_separator()
        file_menu.add_command(label="刪除所選項目", command=self.delete_selected)
        
        
        # 右鍵選單
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="刪除", command=self.delete_selected)

        # 左側面板 - 技能樹顯示
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 技能樹 Treeview
        self.tree = ttk.Treeview(left_frame)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        self.tree.bind("<Button-3>", self.show_context_menu)

        # 右側面板 - 操作區
        right_frame = ttk.Frame(main_frame)
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
        
        ttk.Label(detail_frame, text="技能等級 (0-5):").pack(fill=tk.X, padx=5)
        self.level_spinbox = ttk.Spinbox(detail_frame, from_=0, to=5)
        self.level_spinbox.pack(fill=tk.X, padx=5)
        
        ttk.Label(detail_frame, text="技能經驗 (選填):").pack(fill=tk.X, padx=5)
        self.experience_text = scrolledtext.ScrolledText(detail_frame, height=5)
        self.experience_text.pack(fill=tk.BOTH, expand=True, padx=5)
        
        # 按鈕區
        button_frame = ttk.Frame(right_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(button_frame, text="新增技能", command=self.add_skill).pack(side=tk.LEFT, padx=5)

        # 新增"新增年度資料"按鈕
        self.add_year_button = ttk.Button(button_frame, text="新增年度資料", command=self.add_year_data)
        self.add_year_button.pack(side=tk.LEFT, padx=5)
        self.add_year_button['state'] = 'disabled'  # 初始時停用

        ttk.Button(button_frame, text="更新技能", command=self.update_skill).pack(side=tk.LEFT, padx=5) 
        ttk.Button(button_frame, text="儲存", command=self.save_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="匯入JSON", command=self.import_json).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="匯出JSON", command=self.export_json).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="匯出MM", command=self.export_mm).pack(side=tk.LEFT, padx=5)

        # 設置查詢分頁的內容
        self.setup_search_tab(search_frame)

    def show_context_menu(self, event):
        """顯示右鍵選單"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def update_skill(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("錯誤", "請選擇要更新的技能年份節點")
            return
        
        selected_item = selected[0]
        item_text = self.tree.item(selected_item)['text']
        parent = self.tree.parent(selected_item)
    
        # 找到技能的完整路徑
        path = []
        current = selected_item
        while current:
            path.insert(0, self.tree.item(current)['text'])
            current = self.tree.parent(current)
    
        # 確保選擇的是年份節點
        if len(path) != 4:  # 人員/分類/技能名稱/年份
            messagebox.showerror("錯誤", "請選擇要更新的技能年份節點")
            return
    
        person_name = path[0]
        category = path[1]
        skill_name = path[2]
        year_period = path[3]
    
        # 取得新的技能等級和經驗
        new_level = self.level_spinbox.get()
        new_experience = self.experience_text.get("1.0", tk.END).strip()
    
        try:
            cursor = self.conn.cursor()
        
            # 取得person_id
            cursor.execute("SELECT id FROM persons WHERE name=?", (person_name,))
            person_id = cursor.fetchone()[0]
        
            # 更新資料庫
            cursor.execute("""
                UPDATE skills 
                SET skill_level = ?, experience = ?
                WHERE person_id = ? 
                AND skill_category = ? 
                AND skill_name = ? 
                AND year_period = ?
            """, (new_level, new_experience, person_id, category, skill_name, year_period))
        
            self.conn.commit()
        
            # 更新樹狀圖顯示
            year_id = selected_item
            level_id = f"{year_id}_level"
            exp_id = f"{year_id}_exp"
        
            # 更新或創建等級節點
            if self.tree.exists(level_id):
                self.tree.item(level_id, text=f"技能等級: {new_level}")
            else:
                self.tree.insert(year_id, 'end', level_id, text=f"技能等級: {new_level}")
        
            # 更新或創建經驗節點
            if new_experience:
                if self.tree.exists(exp_id):
                    self.tree.item(exp_id, text=f"技能經驗: {new_experience}")
                else:
                    self.tree.insert(year_id, 'end', exp_id, text=f"技能經驗: {new_experience}")
            else:
                if self.tree.exists(exp_id):
                    self.tree.delete(exp_id)
        
            messagebox.showinfo("成功", "技能資料已更新")
        
        except Exception as e:
            messagebox.showerror("錯誤", f"更新失敗: {str(e)}")

    def delete_selected(self):
        """刪除選中的項目"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("提示", "請先選擇要刪除的項目")
            return

        item = selected[0]
        item_text = self.tree.item(item)['text']
    
        # 確認是否要刪除
        if not messagebox.askyesno("確認刪除", f"確定要刪除 '{item_text}' 嗎？\n這個操作無法復原。"):
            return

        try:
            # 開始交易
            self.conn.execute("BEGIN TRANSACTION")
        
            # 修正這行，移除額外的參數
            depth = len(self.tree.get_children(item))
            parent = self.tree.parent(item)
        
            # 查找根節點（人員名稱）
            root_item = item
            while self.tree.parent(root_item):
                root_item = self.tree.parent(root_item)
            person_name = self.tree.item(root_item)['text']
        
            cursor = self.conn.cursor()
        
            # 取得 person_id
            cursor.execute("SELECT id FROM persons WHERE name = ?", (person_name,))
            person_id = cursor.fetchone()[0]
        
            # 依據不同層級執行不同的刪除邏輯
            if parent == '':  # 第一層：刪除人員
                cursor.execute("DELETE FROM persons WHERE name = ?", (item_text,))
                cursor.execute("DELETE FROM skills WHERE person_id = ?", (person_id,))
                self.tree.delete(item)
            
            else:
                # 解析項目的完整路徑
                path = []
                current = item
                while current:
                    path.insert(0, self.tree.item(current)['text'])
                    current = self.tree.parent(current)
            
                if len(path) == 2:  # 第二層：刪除某分類下的所有技能
                    cursor.execute("""
                        DELETE FROM skills 
                        WHERE person_id = ? AND skill_category = ?
                    """, (person_id, item_text))
                    self.tree.delete(item)
                
                elif len(path) == 3:  # 第三層：刪除特定技能
                    cursor.execute("""
                        DELETE FROM skills 
                        WHERE person_id = ? 
                        AND skill_category = ? 
                        AND skill_name = ?
                    """, (person_id, path[1], item_text))
                    self.tree.delete(item)
                
                elif len(path) == 4:  # 第四層：刪除特定年份的技能記錄
                    cursor.execute("""
                        DELETE FROM skills 
                        WHERE person_id = ? 
                        AND skill_category = ? 
                        AND skill_name = ? 
                        AND year_period = ?
                    """, (person_id, path[1], path[2], item_text))
                    self.tree.delete(item)
                
                elif len(path) == 5:  # 第五層：刪除技能等級或經驗
                    # 取得完整的技能記錄
                    cursor.execute("""
                        SELECT id, skill_level, experience 
                        FROM skills 
                        WHERE person_id = ? 
                        AND skill_category = ? 
                        AND skill_name = ? 
                        AND year_period = ?
                    """, (person_id, path[1], path[2], path[3]))
                    skill_record = cursor.fetchone()
                
                    if skill_record:
                        if "技能等級" in item_text:
                            # 如果刪除技能等級，整條記錄都要刪除
                            cursor.execute("DELETE FROM skills WHERE id = ?", (skill_record[0],))
                            self.tree.delete(self.tree.parent(item))
                        elif "技能經驗" in item_text:
                            # 如果刪除技能經驗，只更新經驗欄位為空
                            cursor.execute("""
                                UPDATE skills 
                                SET experience = '' 
                                WHERE id = ?
                            """, (skill_record[0],))
                            self.tree.delete(item)
        
            # 提交交易
            self.conn.commit()
            messagebox.showinfo("成功", "刪除成功")
        
        except Exception as e:
            # 發生錯誤時回滾交易
            self.conn.rollback()
            messagebox.showerror("錯誤", f"刪除失敗: {str(e)}")

    def export_json(self):
        """匯出所有資料為 JSON 格式"""
        cursor = self.conn.cursor()
        
        # 取得所有人員資料
        cursor.execute("SELECT id, name FROM persons")
        persons = cursor.fetchall()
        
        export_data = {}
        
        for person_id, person_name in persons:
            # 取得該人員的所有技能
            cursor.execute("""
                SELECT skill_category, skill_name, year_period, skill_level, experience
                FROM skills
                WHERE person_id = ?
                ORDER BY skill_category, skill_name, year_period
            """, (person_id,))
            
            skills = cursor.fetchall()
            
            # 組織該人員的技能資料
            person_skills = []
            for skill in skills:
                category, name, year, level, exp = skill
                skill_data = {
                    "category": category,
                    "name": name,
                    "year": year,
                    "level": level,
                    "experience": exp if exp else ""
                }
                person_skills.append(skill_data)
            
            export_data[person_name] = person_skills
        
        # 選擇儲存位置
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="儲存技能資料"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=2)
                messagebox.showinfo("成功", "資料已成功匯出為JSON格式")
            except Exception as e:
                messagebox.showerror("錯誤", f"匯出失敗: {str(e)}")

    def import_json(self):
        """從 JSON 檔案匯入資料"""
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="選擇要匯入的JSON檔案"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            cursor = self.conn.cursor()
            
            # 開始交易
            self.conn.execute("BEGIN TRANSACTION")
            
            try:
                for person_name, skills in import_data.items():
                    # 新增或取得人員ID
                    cursor.execute("INSERT OR IGNORE INTO persons (name) VALUES (?)", (person_name,))
                    cursor.execute("SELECT id FROM persons WHERE name=?", (person_name,))
                    person_id = cursor.fetchone()[0]
                    
                    # 新增技能
                    for skill in skills:
                        cursor.execute("""
                            INSERT INTO skills 
                            (person_id, skill_category, skill_name, year_period, skill_level, experience)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (person_id, 
                             skill['category'],
                             skill['name'],
                             skill['year'],
                             skill['level'],
                             skill['experience']))
                
                # 提交交易
                self.conn.commit()
                
                # 重新載入顯示
                self.tree.delete(*self.tree.get_children())
                self.load_existing_data()
                
                messagebox.showinfo("成功", "資料已成功匯入")
                
            except Exception as e:
                # 發生錯誤時回滾交易
                self.conn.rollback()
                raise e
                
        except Exception as e:
            messagebox.showerror("錯誤", f"匯入失敗: {str(e)}")

#    def on_tree_select(self, event):
#        selected = self.tree.selection()
#        if selected:
#            item = self.tree.item(selected[0])
#            # 找到選中項目的根節點（人員名稱）
#            parent = selected[0]
#            while self.tree.parent(parent):
#                parent = self.tree.parent(parent)
#            
#            # 更新姓名輸入框
#            person_name = self.tree.item(parent)['text']
#            self.name_entry.delete(0, tk.END)
#            self.name_entry.insert(0, person_name)

    def on_tree_select(self, event):
        """當選擇樹狀節點時更新輸入欄位"""
        selected = self.tree.selection()
        if not selected:
            return
        
        item = selected[0]
        item_text = self.tree.item(item)['text']
    
        # 找到選中項目的完整路徑
        path = []
        current = item
        while current:
            path.insert(0, self.tree.item(current)['text'])
            current = self.tree.parent(current)
    
        # 更新姓名輸入框
        if path:
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, path[0])  # 第一個元素是人名

        # 根據選擇的節點類型執行不同操作
        if len(path) == 3:  # [人名, 分類, 技能名稱] - 選中技能名稱
            # 啟用新增年度資料按鈕
            self.add_year_button['state'] = 'normal'
            # 更新技能分類和名稱
            self.category_combobox.set(path[1])
            self.on_category_selected(None)
            self.skill_combobox.set(path[2])
        elif len(path) == 4:  # [人名, 分類, 技能名稱, 年份]
            # 停用新增年度資料按鈕
            self.add_year_button['state'] = 'disabled'

            # 更新技能分類
            self.category_combobox.set(path[1])
        
            # 觸發分類選擇事件以更新技能名稱下拉選單
            self.on_category_selected(None)
        
            # 更新技能名稱
            self.skill_combobox.set(path[2])
        
            # 更新年份
            self.year_entry.delete(0, tk.END)
            self.year_entry.insert(0, path[3])
        
            # 從資料庫獲取該技能的等級和經驗
            try:
                cursor = self.conn.cursor()
                cursor.execute("""
                    SELECT skill_level, experience
                    FROM skills
                    JOIN persons ON skills.person_id = persons.id
                    WHERE persons.name = ?
                    AND skill_category = ?
                    AND skill_name = ?
                    AND year_period = ?
                """, (path[0], path[1], path[2], path[3]))
            
                result = cursor.fetchone()
                if result:
                    level, experience = result
                    # 更新技能等級
                    self.level_spinbox.delete(0, tk.END)
                    self.level_spinbox.insert(0, level)
                
                    # 更新技能經驗
                    self.experience_text.delete('1.0', tk.END)
                    if experience:
                        self.experience_text.insert('1.0', experience)
            except Exception as e:
                messagebox.showerror("錯誤", f"載入技能資料失敗: {str(e)}")


    def add_year_data(self):
        """新增年度資料的功能"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("錯誤", "請先選擇技能")
            return

        # 取得選中項目的路徑資訊
        path = []
        current = selected[0]
        while current:
            path.insert(0, self.tree.item(current)['text'])
            current = self.tree.parent(current)

        if len(path) != 3:
            messagebox.showerror("錯誤", "請先選擇技能名稱")
            return

        person_name, category, skill_name = path
    
        # 直接使用選中的節點作為 skill_id
        skill_id = selected[0]

        #person_name = path[0]
        #category = path[1]
        #skill_name = path[2]
    
        year_period = self.year_entry.get().strip()
        skill_level = self.level_spinbox.get()
        experience = self.experience_text.get("1.0", tk.END).strip()

        if not year_period:
            messagebox.showerror("錯誤", "請輸入年度期間")
            return

        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 1 FROM skills s
            JOIN persons p ON s.person_id = p.id
            WHERE p.name = ? AND s.skill_category = ? 
            AND s.skill_name = ? AND s.year_period = ?
        """, (person_name, category, skill_name, year_period))

        if cursor.fetchone():
            messagebox.showerror("錯誤", f"已存在 {year_period} 的技能資料")
            return

        try:
            cursor.execute("SELECT id FROM persons WHERE name = ?", (person_name,))
            person_id = cursor.fetchone()[0]

            cursor.execute("""
                INSERT INTO skills (person_id, skill_category, skill_name, year_period, skill_level, experience)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (person_id, category, skill_name, year_period, skill_level, experience))

            self.conn.commit()

            # 插入年度節點時進行排序
            skill_id = selected[0]
            # 修改 year_id 的生成方式
            year_id = f"{person_name}_{category}_{skill_name}_{year_period}"
        
            skill_node = skill_id
            year_position = 'end'

            # 取得所有現有的年度節點
            existing_years = []
            for child in self.tree.get_children(skill_id):
                year_text = self.tree.item(child)['text']
                print(f"Child: {child}, Text: {year_text}")
                existing_years.append((year_text, child))
        
            # 將新年度加入並排序
            existing_years.append((year_period, None))
            sorted_years = self.sort_years(existing_years)

            # 找到新年度應該插入的位置
            insert_pos = 0
            for i, (year, _) in enumerate(sorted_years):
                if year == year_period:
                    insert_pos = i
                    break
        
            # 如果不是要插在最後，則找到要插入位置的前一個節點
            if insert_pos < len(sorted_years) - 1:
                year_position = sorted_years[insert_pos + 1][1]
            else:
                year_position = 'end'

            # 插入新年度節點
            year_node = self.tree.insert(skill_id, insert_pos, year_id, text=year_period)
            self.tree.insert(year_node, 'end', f"{year_id}_level", text=f"技能等級: {skill_level}")
            if experience:
                self.tree.insert(year_node, 'end', f"{year_id}_exp", text=f"技能經驗: {experience}")

            messagebox.showinfo("成功", f"已新增 {year_period} 的技能資料")

            # 清空輸入欄位
            self.year_entry.delete(0, tk.END)
            self.level_spinbox.delete(0, tk.END)
            self.level_spinbox.insert(0, "1")
            self.experience_text.delete("1.0", tk.END)

        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("錯誤", f"新增年度資料失敗: {str(e)}")

    def sort_years(self, years):
        """排序年度資料，考慮年度和半年度格式"""
        def year_key(year_tuple):
            year = year_tuple[0]
            if 'H1' in year:
                return year.replace('H1', '') + '1'
            elif 'H2' in year:
                return year.replace('H2', '') + '2'
            return year
    
        return sorted(years, key=year_key)


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

        # 插入年度節點時進行排序
        skill_node = skill_id
        year_position = 'end'
    
        # 取得所有現有的年度節點
        existing_years = []
        for child in self.tree.get_children(skill_node):
            year_text = self.tree.item(child)['text']
            existing_years.append((year_text, child))
    
        # 將新年度加入並排序
        existing_years.append((year_period, None))
        sorted_years = self.sort_years(existing_years)
    
        # 找到新年度應該插入的位置
        insert_pos = 0
        for i, (year, _) in enumerate(sorted_years):
            if year == year_period:
                insert_pos = i
                break
    
        # 如果不是要插在最後，則找到要插入位置的前一個節點
        if insert_pos < len(sorted_years) - 1:
            year_position = sorted_years[insert_pos + 1][1]
    
        # 插入新年度節點

        print(f"skill_id: {skill_node}")
        print(f"year_position: {year_position}")
        print(f"year_id: {year_id}")

        year_node = self.tree.insert(skill_node, year_position, year_id, text=year_period)
        self.tree.insert(year_node, 'end', f"{year_id}_level", text=f"技能等級: {skill_level}")
        if experience:
            self.tree.insert(year_node, 'end', f"{year_id}_exp", text=f"技能經驗: {experience}")
            
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

#===========================================
#  
#===========================================
    def setup_search_tab(self, parent):
        """設置查詢分頁"""
        # 查詢條件區域
        search_criteria_frame = ttk.LabelFrame(parent, text="查詢條件")
        search_criteria_frame.pack(fill=tk.X, padx=5, pady=5)

        # 技能名稱選擇
        skill_frame = ttk.Frame(search_criteria_frame)
        skill_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(skill_frame, text="技能分類:").pack(side=tk.LEFT, padx=5)
        self.search_category_combobox = ttk.Combobox(skill_frame, values=list(self.skill_types.keys()))
        self.search_category_combobox.pack(side=tk.LEFT, padx=5)
        self.search_category_combobox.bind('<<ComboboxSelected>>', self.on_search_category_selected)
        
        ttk.Label(skill_frame, text="技能名稱:").pack(side=tk.LEFT, padx=5)
        self.search_skill_combobox = ttk.Combobox(skill_frame)
        self.search_skill_combobox.pack(side=tk.LEFT, padx=5)
        
        # 年份期間
        year_frame = ttk.Frame(search_criteria_frame)
        year_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(year_frame, text="年份期間:").pack(side=tk.LEFT, padx=5)
        self.search_year_entry = ttk.Entry(year_frame)
        self.search_year_entry.pack(side=tk.LEFT, padx=5)
        
        # 查詢按鈕
        ttk.Button(search_criteria_frame, text="查詢", command=self.perform_search).pack(pady=10)

        # 查詢結果顯示區域
        result_frame = ttk.LabelFrame(parent, text="查詢結果")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
        # 建立結果顯示的表格，設定較高的 row height
        columns = ('name', 'skill_level', 'experience')
        self.result_tree = ttk.Treeview(result_frame, columns=columns, show='headings', 
                                   height=10)  # 限制顯示行數，避免過度展開
    
        # 設定欄位標題和寬度
        self.result_tree.heading('name', text='人員姓名')
        self.result_tree.heading('skill_level', text='技能等級')
        self.result_tree.heading('experience', text='技能經驗')
    
        # 調整欄位寬度
        self.result_tree.column('name', width=100, stretch=False)
        self.result_tree.column('skill_level', width=60, stretch=False)
        self.result_tree.column('experience', width=600, stretch=True)  # 技能經驗欄位可伸縮
    
        # 設定每個項目的最小高度
        #style = ttk.Style()
        #style.configure('Treeview', rowheight=60)  # 設定較大的行高以容納多行文字
    
        # 添加垂直和水平捲軸
        vsb = ttk.Scrollbar(result_frame, orient="vertical", command=self.result_tree.yview)
        hsb = ttk.Scrollbar(result_frame, orient="horizontal", command=self.result_tree.xview)
        self.result_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    
        # 使用網格布局來放置表格和捲軸
        self.result_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
    
        # 配置grid權重，使表格可以跟隨視窗調整大小
        result_frame.grid_rowconfigure(0, weight=1)
        result_frame.grid_columnconfigure(0, weight=1)

    def on_search_category_selected(self, event):
        """當查詢分頁中選擇技能分類時更新技能名稱選項"""
        category = self.search_category_combobox.get()
        if category in self.skill_types:
            self.search_skill_combobox['values'] = self.skill_types[category]
            if self.skill_types[category]:
                self.search_skill_combobox.set(self.skill_types[category][0])

    def perform_search(self):
        """執行查詢"""
        # 清空現有結果
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
            
        # 獲取查詢條件
        skill_category = self.search_category_combobox.get()
        skill_name = self.search_skill_combobox.get()
        year_period = self.search_year_entry.get()
        
        # 驗證輸入
        if not all([skill_category, skill_name, year_period]):
            messagebox.showerror("錯誤", "請填寫所有查詢條件")
            return
            
        try:
            cursor = self.conn.cursor()
            # 執行查詢
            cursor.execute("""
                SELECT DISTINCT p.name, s.skill_level, s.experience
                FROM persons p
                JOIN skills s ON p.id = s.person_id
                WHERE s.skill_category = ? 
                AND s.skill_name = ?
                AND s.year_period = ?
                ORDER BY p.name
            """, (skill_category, skill_name, year_period))
            
            results = cursor.fetchall()
            
            if not results:
                messagebox.showinfo("查詢結果", "沒有找到符合條件的資料")
                return
                
            # 顯示結果
            #for name, level, experience in results:
            #    self.result_tree.insert('', 'end', values=(name, level, experience or ""))
            # 顯示結果，對技能經驗進行處理
            #for name, level, experience in results:
            #    # 如果經驗內容過長，截斷並添加省略號
            #    display_exp = experience if experience else ""
            #    if len(display_exp) > 50:  # 設定顯示長度閾值
            #        display_exp = display_exp[:47] + "..."
            #    
            #    self.result_tree.insert('', 'end', values=(name, level, display_exp))

            # 顯示結果，處理多行文字
            for name, level, experience in results:
                # 格式化經驗文字：每30個字元換行
                if experience:
                    formatted_exp = self.format_experience_text(experience)
                else:
                    formatted_exp = ""
                
                # 插入資料
                self.result_tree.insert('', 'end', values=(name, level, formatted_exp))


        except Exception as e:
            messagebox.showerror("錯誤", f"查詢失敗: {str(e)}")


    # 新增格式化經驗文字的方法
    def format_experience_text(self, text):
        """將長文字格式化為多行顯示"""
        if not text:
            return ""
        
        # 將原有的換行符保留
        paragraphs = text.split('\n')
        formatted_paragraphs = []
    
        for paragraph in paragraphs:
            # 如果段落超過40個字元，進行換行處理
            if len(paragraph) > 40:
                # 將段落分割成最大長度為40的部分
                parts = [paragraph[i:i+40] for i in range(0, len(paragraph), 40)]
                formatted_paragraphs.extend(parts)
            else:
                formatted_paragraphs.append(paragraph)
    
        # 使用換行符合併所有行
        return '\n'.join(formatted_paragraphs)

if __name__ == "__main__":
    root = tk.Tk()
    app = SkillTreeManager(root)
    root.mainloop()



    