import tkinter as tk
from tkinter import ttk, messagebox, filedialog
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

    # ... [前面的方法保持不變] ...

    def setup_gui(self):
        # 主選單
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 檔案選單
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="檔案", menu=file_menu)
        file_menu.add_command(label="匯出JSON", command=self.export_json)
        file_menu.add_command(label="匯入JSON", command=self.import_json)
        file_menu.add_separator()
        file_menu.add_command(label="匯出MM", command=self.export_mm)
        
        # ... [其餘的 GUI 設置保持不變] ...

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

    # ... [其他方法保持不變] ...

if __name__ == "__main__":
    root = tk.Tk()
    app = SkillTreeManager(root)
    root.mainloop()