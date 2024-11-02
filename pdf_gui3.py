import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import NameObject, create_string_object
from PyPDF2.constants import UserAccessPermissions
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from io import BytesIO


class PDFToolGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF工具")
        self.root.geometry("600x750")
        
        # 建立主捲動框架
        self.main_canvas = tk.Canvas(root)
        self.scrollbar = ttk.Scrollbar(root, orient="vertical", command=self.main_canvas.yview)
        self.scrollable_frame = ttk.Frame(self.main_canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.main_canvas.configure(
                scrollregion=self.main_canvas.bbox("all")
            )
        )

        self.main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.main_canvas.configure(yscrollcommand=self.scrollbar.set)

        # 設置主框架
        main_frame = ttk.Frame(self.scrollable_frame, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 文件選擇
        ttk.Label(main_frame, text="輸入PDF檔案:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.input_path = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.input_path, width=50).grid(row=0, column=1, pady=5)
        ttk.Button(main_frame, text="瀏覽", command=self.browse_input).grid(row=0, column=2, pady=5)
        
        ttk.Label(main_frame, text="輸出PDF檔案:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.output_path = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.output_path, width=50).grid(row=1, column=1, pady=5)
        ttk.Button(main_frame, text="瀏覽", command=self.browse_output).grid(row=1, column=2, pady=5)
        
        # 浮水印設定
        watermark_frame = ttk.LabelFrame(main_frame, text="浮水印設定", padding="5")
        watermark_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # 新增勾選方塊
        self.use_text_watermark = tk.BooleanVar(value=False)
        ttk.Checkbutton(watermark_frame, text="啟用文字浮水印", 
                       variable=self.use_text_watermark).grid(row=0, column=0, sticky=tk.W)
        self.watermark_text = tk.StringVar()
        ttk.Entry(watermark_frame, textvariable=self.watermark_text, width=40).grid(row=0, column=1, columnspan=2)
        
        self.use_image_watermark = tk.BooleanVar(value=False)
        ttk.Checkbutton(watermark_frame, text="啟用圖片浮水印", 
                       variable=self.use_image_watermark).grid(row=1, column=0, sticky=tk.W)
        self.watermark_image = tk.StringVar()
        ttk.Entry(watermark_frame, textvariable=self.watermark_image, width=40).grid(row=1, column=1)
        ttk.Button(watermark_frame, text="瀏覽", command=self.browse_image).grid(row=1, column=2)
        
        # 浮水印參數
        params_frame = ttk.LabelFrame(main_frame, text="浮水印參數", padding="5")
        params_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # 字體大小
        ttk.Label(params_frame, text="字體大小:").grid(row=0, column=0, sticky=tk.W)
        self.font_size = tk.IntVar(value=60)
        self.font_size_spinbox = ttk.Spinbox(params_frame, from_=1, to=200, textvariable=self.font_size, width=8)
        self.font_size_spinbox.grid(row=0, column=1)
        
        # 旋轉角度
        ttk.Label(params_frame, text="旋轉角度:").grid(row=1, column=0, sticky=tk.W)
        self.rotation = tk.DoubleVar(value=0)
        self.rotation_spinbox = ttk.Spinbox(params_frame, from_=0, to=360, textvariable=self.rotation, width=8)
        self.rotation_spinbox.grid(row=1, column=1)
        
        # 圖片位置
        ttk.Label(params_frame, text="圖片位置 (x, y):").grid(row=2, column=0, sticky=tk.W)
        self.image_x = tk.DoubleVar(value=0.25)
        self.image_y = tk.DoubleVar(value=0.25)
        self.image_x_spinbox = ttk.Spinbox(params_frame, from_=0, to=1, increment=0.1, textvariable=self.image_x, width=8)
        self.image_y_spinbox = ttk.Spinbox(params_frame, from_=0, to=1, increment=0.1, textvariable=self.image_y, width=8)
        self.image_x_spinbox.grid(row=2, column=1)
        self.image_y_spinbox.grid(row=2, column=2)
        
        # 圖片大小
        ttk.Label(params_frame, text="圖片大小 (寬, 高):").grid(row=3, column=0, sticky=tk.W)
        self.image_width = tk.DoubleVar(value=0.5)
        self.image_height = tk.DoubleVar(value=0.5)
        self.image_width_spinbox = ttk.Spinbox(params_frame, from_=0, to=1, increment=0.1, textvariable=self.image_width, width=8)
        self.image_height_spinbox = ttk.Spinbox(params_frame, from_=0, to=1, increment=0.1, textvariable=self.image_height, width=8)
        self.image_width_spinbox.grid(row=3, column=1)
        self.image_height_spinbox.grid(row=3, column=2)
        
        # 透明度
        ttk.Label(params_frame, text="圖片透明度:").grid(row=4, column=0, sticky=tk.W)
        self.image_opacity = tk.DoubleVar(value=0.5)
        self.opacity_spinbox = ttk.Spinbox(params_frame, from_=0, to=1, increment=0.1, textvariable=self.image_opacity, width=8)
        self.opacity_spinbox.grid(row=4, column=1)
        
        # 安全設定
        security_frame = ttk.LabelFrame(main_frame, text="安全設定", padding="5")
        security_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(security_frame, text="開啟密碼:").grid(row=0, column=0, sticky=tk.W)
        self.password = tk.StringVar()
        ttk.Entry(security_frame, textvariable=self.password, show="*").grid(row=0, column=1)
        
        ttk.Label(security_frame, text="擁有者密碼:").grid(row=1, column=0, sticky=tk.W)
        self.owner_password = tk.StringVar()
        ttk.Entry(security_frame, textvariable=self.owner_password, show="*").grid(row=1, column=1)
        
        self.restrict_permissions = tk.BooleanVar()
        ttk.Checkbutton(security_frame, text="限制權限（禁止列印和編輯）", 
                        variable=self.restrict_permissions).grid(row=2, column=0, columnspan=2)
        
        # 頁面選擇
        ttk.Label(main_frame, text="處理頁面 (例如: 1,3,5):").grid(row=5, column=0, sticky=tk.W)
        self.pages = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.pages).grid(row=5, column=1)
        
        # 執行按鈕
        ttk.Button(main_frame, text="執行", command=self.process_pdf).grid(row=6, column=0, columnspan=3, pady=20)

        # 配置捲動條
        self.main_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def validate_inputs(self):
        """驗證輸入值"""
        if not self.input_path.get():
            messagebox.showerror("錯誤", "請選擇輸入PDF檔案")
            return False
        
        if not self.output_path.get():
            messagebox.showerror("錯誤", "請選擇輸出PDF檔案位置")
            return False
        
        if not os.path.exists(self.input_path.get()):
            messagebox.showerror("錯誤", "輸入PDF檔案不存在")
            return False
        
        if self.watermark_image.get() and not os.path.exists(self.watermark_image.get()):
            messagebox.showerror("錯誤", "浮水印圖片不存在")
            return False
        
        return True

    def browse_input(self):
        filename = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if filename:
            self.input_path.set(filename)
            # 修改自動設定輸出檔案名稱的邏輯
            output_dir = os.path.dirname(filename)
            base_name = os.path.splitext(os.path.basename(filename))[0]
            output_name = f"{base_name}_gen.pdf"
            self.output_path.set(os.path.join(output_dir, output_name))
    
    def browse_output(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile="output.pdf"
        )
        if filename:
            self.output_path.set(filename)
    
    def browse_image(self):
        filename = filedialog.askopenfilename(
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.watermark_image.set(filename)

    def process_pdf(self):
        if not self.validate_inputs():
            return
            
        try:
            # 處理頁面參數
            pages = None
            if self.pages.get().strip():
                try:
                    pages = [int(p.strip()) for p in self.pages.get().split(',')]
                except ValueError:
                    messagebox.showerror("錯誤", "頁面格式錯誤，請使用逗號分隔的數字")
                    return
            
            # 修改調用PDF處理函數的參數
            add_watermark(
                self.input_path.get(),
                self.output_path.get(),
                watermark_text=self.watermark_text.get() if self.use_text_watermark.get() else None,
                watermark_image=self.watermark_image.get() if self.use_image_watermark.get() else None,
                pages=pages,
                password=self.password.get() if self.password.get() else "",
                restrict_permissions=self.restrict_permissions.get(),
                owner_password=self.owner_password.get() if self.owner_password.get() else None,
                font_size=self.font_size.get(),
                rotation=self.rotation.get(),
                image_position=(self.image_x.get(), self.image_y.get()),
                image_size=(self.image_width.get(), self.image_height.get()),
                image_opacity=self.image_opacity.get()
            )
            messagebox.showinfo("成功", "PDF處理完成！")
        except Exception as e:
            messagebox.showerror("錯誤", f"處理過程中發生錯誤：\n{str(e)}")



def add_watermark(input_pdf, output_pdf, watermark_text=None, watermark_image=None, pages=None, password="", 
                 restrict_permissions=False, owner_password=None, font_size=60, rotation=0, 
                 image_position=(0.25, 0.25), image_size=(0.5, 0.5), image_opacity=0.5):
    try:
        reader = PdfReader(input_pdf)
        writer = PdfWriter()

        if watermark_text or watermark_image:
            watermark_pdf = BytesIO()
            can = canvas.Canvas(watermark_pdf, pagesize=letter)
            width, height = letter

            if watermark_text:
                can.saveState()
                can.translate(width/2, height/2)
                can.rotate(rotation)
                can.setFont("Helvetica", font_size)
                can.setFillColorRGB(0.5, 0.5, 0.5, 0.3)
                can.drawCentredString(0, 0, watermark_text)
                can.restoreState()
            elif watermark_image:
                img_width = width * image_size[0]
                img_height = height * image_size[1]
                x = width * image_position[0]
                y = height * image_position[1]
                can.saveState()
                can.setFillAlpha(image_opacity)
                can.drawImage(watermark_image, x, y, width=img_width, height=img_height, mask='auto')
                can.restoreState()

            can.save()
            watermark = PdfReader(watermark_pdf).pages[0]

        for i, page in enumerate(reader.pages):
            if not pages or (i + 1) in pages:
                if watermark_text or watermark_image:
                    page.merge_page(watermark)
            writer.add_page(page)

        if password or restrict_permissions:
            if restrict_permissions:
                # 設定受限的權限
                permissions = UserAccessPermissions.FILL_FORM_FIELDS  # 只允許填寫表單
            else:
                # 設定完整的權限
                permissions = (UserAccessPermissions.PRINT | 
                             UserAccessPermissions.MODIFY | 
                             UserAccessPermissions.EXTRACT | 
                             UserAccessPermissions.ADD_OR_MODIFY |
                             UserAccessPermissions.FILL_FORM_FIELDS | 
                             UserAccessPermissions.EXTRACT_TEXT_AND_GRAPHICS |
                             UserAccessPermissions.ASSEMBLE_DOC |
                             UserAccessPermissions.PRINT_TO_REPRESENTATION)

            writer.encrypt(
                #user_password=password if password else None,
                user_password=password,
                owner_password=owner_password if owner_password else (password if password else 'owner'),
                #owner_password=owner_password,
                use_128bit=True,
                permissions_flag=permissions
            )

        with open(output_pdf, "wb") as output_file:
            writer.write(output_file)

    except Exception as e:
        raise Exception(f"PDF處理失敗: {str(e)}")


def main():
    root = tk.Tk()
    app = PDFToolGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()