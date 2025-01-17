# ... [前面的 import 保持不變] ...

class SkillTreeManager:
    def __init__(self, root):
        # ... [其他初始化保持不變] ...
        self.selected_item = None  # 追踪當前選中的項目

    def setup_gui(self):
        # ... [前面的 GUI 設置保持不變到 menubar 部分] ...

        # 在檔案選單中添加刪除功能
        file_menu.add_separator()
        file_menu.add_command(label="刪除所選項目", command=self.delete_selected)
        
        # 右鍵選單
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="刪除", command=self.delete_selected)
        
        # 在樹狀圖中綁定右鍵選單
        self.tree.bind("<Button-3>", self.show_context_menu)
        
        # ... [其餘的 GUI 設置保持不變] ...

    def show_context_menu(self, event):
        """顯示右鍵選單"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

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
            
            # 根據項目的深度決定刪除方式
            depth = len(self.tree.get_children('', item))
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

    # ... [其他方法保持不變] ...

if __name__ == "__main__":
    root = tk.Tk()
    app = SkillTreeManager(root)
    root.mainloop()