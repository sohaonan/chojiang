import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import random
import csv
from docx import Document
import os
import shutil
import time
import threading
import json
import sys
from PIL import Image, ImageTk

def resource_path(relative_path):
    """ 获取资源的绝对路径 """
    try:
        # PyInstaller创建临时文件夹,将路径存储在_MEIPASS中
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class LoginWindow:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent.root)
        self.window.title("管理员验证")
        self.window.geometry("300x200")  # 增加窗口高度
        self.window.transient(parent.root)
        self.window.grab_set()
        
        # 加载配置
        self.load_config()
        
        # 创建登录界面
        self.create_widgets()
        
        # 窗口居中
        self.center_window()
        
    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(expand=True, fill='both')
        
        # 密码
        ttk.Label(main_frame, text="管理密码:", font=('Arial', 12)).pack(fill='x', pady=5)
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(main_frame, textvariable=self.password_var, show="*", font=('Arial', 12))
        self.password_entry.pack(fill='x', pady=10)  # 增加垂直间距
        
        # 登录按钮
        login_btn = ttk.Button(main_frame, text="确认", command=self.login)
        login_btn.pack(fill='x', pady=20)
        
        # 绑定回车键
        self.password_entry.bind('<Return>', lambda e: self.login())
        
        # 初始焦点
        self.password_entry.focus()
        
    def load_config(self):
        try:
            config_path = resource_path("config.json")
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except Exception as e:
            messagebox.showerror("错误", f"加载配置文件失败: {str(e)}")
            self.config = {"admin": {"password": "123456"}}
            
    def login(self):
        password = self.password_var.get().strip()  # 添加strip()去除空白字符
        
        if not password:
            messagebox.showwarning("警告", "请输入管理密码！")
            return
            
        try:
            correct_password = self.config['admin']['password'].strip()  # 添加strip()去除空白字符
            if password == correct_password:
                self.window.destroy()
                self.parent.is_logged_in = True
                self.parent.notebook.select(1)  # 切换到管理标签
            else:
                messagebox.showerror("错误", "管理密码错误！")
                self.password_var.set("")
                self.password_entry.focus()
        except KeyError:
            messagebox.showerror("错误", "配置文件格式错误！")
            self.window.destroy()
            
    def center_window(self):
        self.window.update()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')

class LotterySystem:
    def __init__(self, root):
        self.root = root
        self.root.title("抽奖系统")
        self.root.geometry("1200x800")
        
        # 设置主题色
        self.primary_color = "#4a90e2"
        self.secondary_color = "#f5f5f5"
        self.accent_color = "#e74c3c"
        self.button_color = "#2ecc71"
        self.button_hover_color = "#27ae60"
        
        # 初始化数据库
        self.init_database()
        
        # 创建主界面
        self.init_ui()
        
        # 抽奖动画控制
        self.is_rolling = False
        self.current_names = []
        self.current_index = 0
        
        # 添加窗口关闭事件处理
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def init_database(self):
        self.conn = sqlite3.connect('lottery.db')
        self.cursor = self.conn.cursor()
        
        # 创建奖池表（移除max_winners字段）
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS pools (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        ''')
        
        # 创建参与者表（添加is_whitelist字段）
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS participants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                pool_id INTEGER,
                is_whitelist BOOLEAN DEFAULT 0,
                FOREIGN KEY (pool_id) REFERENCES pools(id)
            )
        ''')
        
        self.conn.commit()
        
    def init_ui(self):
        # 设置样式
        self.setup_styles()
        
        # 创建标签页
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=5)
        
        # 绑定标签页切换事件
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_changed)
        
        # 抽奖页面
        self.lottery_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.lottery_tab, text="抽奖")
        
        # 管理页面
        self.manage_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.manage_tab, text="管理")
        
        # 初始化组件
        self.pool_combo = ttk.Combobox(state='readonly')
        self.import_pool_combo = ttk.Combobox(state='readonly')
        
        self.setup_lottery_tab()
        self.setup_manage_tab()
        
        # 默认选择抽奖标签
        self.notebook.select(0)
        
        # 记录登录状态
        self.is_logged_in = False
        
    def setup_styles(self):
        style = ttk.Style()
        
        # 配置标签页样式
        style.configure('TNotebook', background=self.secondary_color)
        style.configure('TNotebook.Tab', padding=[20, 10], font=('Arial', 12))
        
        # 配置标签框架样式
        style.configure('TLabelframe', background=self.secondary_color)
        style.configure('TLabelframe.Label', font=('Arial', 14, 'bold'), foreground=self.primary_color)
        
        # 配置按钮样式
        style.configure('Accent.TButton', 
                       font=('Arial', 16, 'bold'),
                       padding=[30, 15],
                       background=self.button_color,
                       foreground='white')
        
        # 配置下拉框样式
        style.configure('TCombobox', 
                       font=('Arial', 14),
                       padding=5,
                       selectbackground=self.primary_color)
        
        # 配置数字输入框样式
        style.configure('TSpinbox', 
                       font=('Arial', 14),
                       padding=5)
        
    def setup_lottery_tab(self):
        # 创建主框架
        self.lottery_main_frame = ttk.Frame(self.lottery_tab)
        self.lottery_main_frame.pack(expand=True, fill='both')
        
        # 创建设置页面
        self.setup_frame = ttk.Frame(self.lottery_main_frame)
        self.setup_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # 标题
        title_frame = ttk.Frame(self.setup_frame)
        title_frame.pack(fill='x', pady=20)
        
        title_label = ttk.Label(title_frame, 
                              text="幸运抽奖",
                              font=('Arial', 48, 'bold'),
                              foreground=self.primary_color)
        title_label.pack()
        
        subtitle_label = ttk.Label(title_frame,
                                 text="让我们一起见证幸运时刻",
                                 font=('Arial', 16),
                                 foreground='#666666')
        subtitle_label.pack(pady=10)
        
        # 抽奖设置框架
        settings_frame = ttk.LabelFrame(self.setup_frame, text="抽奖设置", padding=20)
        settings_frame.pack(fill='x', pady=20)
        
        # 选择抽奖池
        pool_frame = ttk.Frame(settings_frame)
        pool_frame.pack(fill='x', pady=10)
        ttk.Label(pool_frame, 
                 text="选择抽奖池:",
                 font=('Arial', 14),
                 foreground='#333333').pack(side='left', padx=5)
        
        # 创建奖池下拉框
        self.pool_var = tk.StringVar()
        self.pool_combo = ttk.Combobox(pool_frame,
                                     textvariable=self.pool_var,
                                     state='readonly',
                                     font=('Arial', 14),
                                     width=30)
        self.pool_combo.pack(side='left', padx=5)
        
        # 抽奖人数
        count_frame = ttk.Frame(settings_frame)
        count_frame.pack(fill='x', pady=10)
        ttk.Label(count_frame,
                 text="抽奖人数:",
                 font=('Arial', 14),
                 foreground='#333333').pack(side='left', padx=5)
        self.count_spin = ttk.Spinbox(count_frame,
                                    from_=1,
                                    to=100,
                                    width=5,
                                    font=('Arial', 14))
        self.count_spin.set(1)
        self.count_spin.pack(side='left', padx=5)
        
        # 开始抽奖按钮
        button_frame = ttk.Frame(settings_frame)
        button_frame.pack(fill='x', pady=20)
        
        self.start_btn = tk.Button(button_frame,
                                 text="开始抽奖",
                                 command=self.start_lottery,
                                 font=('Arial', 16, 'bold'),
                                 bg='#FF4757',
                                 fg='white',
                                 padx=30,
                                 pady=10,
                                 relief=tk.RAISED,
                                 borderwidth=2,
                                 cursor='hand2')
        
        # 设置按钮效果
        def on_enter(e):
            self.start_btn.config(
                bg='#FF6B81',
                relief=tk.SUNKEN,
                borderwidth=3
            )
            
        def on_leave(e):
            self.start_btn.config(
                bg='#FF4757',
                relief=tk.RAISED,
                borderwidth=2
            )
            
        self.start_btn.bind('<Enter>', on_enter)
        self.start_btn.bind('<Leave>', on_leave)
        self.start_btn.pack(pady=5)
        
        # 创建抽奖动画页面
        self.lottery_frame = ttk.Frame(self.lottery_main_frame)
        
        # 滚动显示区域
        self.rolling_label = ttk.Label(self.lottery_frame,
                                     text="准备开始",
                                     font=('Arial', 72, 'bold'),
                                     foreground=self.primary_color)
        self.rolling_label.pack(expand=True)
        
        # 创建结果显示页面
        self.result_frame = ttk.Frame(self.lottery_main_frame)
        
        # 结果标题
        self.result_title = ttk.Label(self.result_frame,
                                    text="🎉 恭喜以下幸运者 🎉",
                                    font=('Arial', 36, 'bold'),
                                    foreground=self.primary_color)
        self.result_title.pack(pady=20)
        
        # 结果显示区域
        self.result_text = tk.Text(self.result_frame,
                                 font=('Arial', 24),
                                 foreground=self.accent_color,
                                 wrap=tk.WORD,
                                 height=10,
                                 width=40,
                                 bd=0)
        self.result_text.pack(expand=True, fill='both', pady=10)
        
        # 返回设置按钮
        self.back_btn = tk.Button(self.result_frame,
                                text="返回设置",
                                command=self.show_setup,
                                font=('Arial', 14),
                                bg='#2ecc71',
                                fg='white',
                                padx=20,
                                pady=5,
                                relief=tk.RAISED,
                                borderwidth=2,
                                cursor='hand2')
        self.back_btn.pack(pady=20)
        
        # 刷新奖池列表
        self.refresh_lottery_pools()
        
    def show_setup(self):
        """显示设置页面"""
        self.result_frame.pack_forget()
        self.lottery_frame.pack_forget()
        self.setup_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
    def show_lottery(self):
        """显示抽奖动画页面"""
        self.setup_frame.pack_forget()
        self.result_frame.pack_forget()
        self.lottery_frame.pack(expand=True, fill='both')
        
    def show_result(self):
        """显示结果页面"""
        self.setup_frame.pack_forget()
        self.lottery_frame.pack_forget()
        self.result_frame.pack(expand=True, fill='both', padx=20, pady=20)

    def refresh_lottery_pools(self):
        """刷新抽奖页面的奖池下拉框"""
        self.cursor.execute('''
            SELECT 
                p.id, 
                p.name, 
                COUNT(pt1.id) as total_count
            FROM pools p
            LEFT JOIN participants pt1 ON p.id = pt1.pool_id
            GROUP BY p.id, p.name
        ''')
        pools = self.cursor.fetchall()
        
        # 更新下拉框选项
        pool_values = []
        for pool in pools:
            pool_id, name, total_count = pool
            if total_count is None:  # 如果奖池为空
                pool_values.append(f"{name} (总人数: 0)")
            else:
                pool_values.append(f"{name} (总人数: {total_count})")
        
        self.pool_combo['values'] = pool_values
        
        # 如果之前有选中的奖池，保持选中状态
        if self.pool_combo.current() != -1:
            self.pool_combo.current(self.pool_combo.current())

    def setup_manage_tab(self):
        """设置管理页面"""
        # 创建左右分栏
        paned = ttk.PanedWindow(self.manage_tab, orient=tk.HORIZONTAL)
        paned.pack(expand=True, fill='both', padx=10, pady=10)
        
        # 左侧奖池列表框架
        left_frame = ttk.LabelFrame(paned, text="奖池列表")
        paned.add(left_frame, weight=1)
        
        # 奖池列表
        self.pool_tree = ttk.Treeview(left_frame, columns=('id', 'name', 'count'), show='headings', height=15)
        self.pool_tree.heading('id', text='ID', anchor='center')
        self.pool_tree.heading('name', text='奖池名称', anchor='center')
        self.pool_tree.heading('count', text='人数', anchor='center')
        self.pool_tree.column('id', width=50, anchor='center')
        self.pool_tree.column('name', width=150, anchor='center')
        self.pool_tree.column('count', width=80, anchor='center')
        self.pool_tree.pack(side='left', fill='both', expand=True)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=self.pool_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.pool_tree.configure(yscrollcommand=scrollbar.set)
        
        # 右侧详情框架
        right_frame = ttk.LabelFrame(paned, text="详情")
        paned.add(right_frame, weight=2)
        
        # 奖池操作框架
        pool_ops_frame = ttk.Frame(right_frame)
        pool_ops_frame.pack(fill='x', padx=5, pady=5)
        
        # 奖池名称输入
        ttk.Label(pool_ops_frame, text="奖池名称:").pack(side='left', padx=5)
        self.pool_name_var = tk.StringVar()
        self.pool_name_entry = ttk.Entry(pool_ops_frame, textvariable=self.pool_name_var)
        self.pool_name_entry.pack(side='left', padx=5)
        
        # 奖池操作按钮
        ttk.Button(pool_ops_frame, text="新增奖池", command=self.add_pool).pack(side='left', padx=5)
        ttk.Button(pool_ops_frame, text="删除奖池", command=self.delete_pool).pack(side='left', padx=5)
        ttk.Button(pool_ops_frame, text="重命名", command=self.rename_pool).pack(side='left', padx=5)
        
        # 参与者列表框架
        participants_frame = ttk.LabelFrame(right_frame, text="参与者列表")
        participants_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 参与者列表
        self.participant_tree = ttk.Treeview(participants_frame, 
                                           columns=('id', 'name', 'whitelist'),
                                           show='headings',
                                           height=10)
        self.participant_tree.heading('id', text='ID', anchor='center')
        self.participant_tree.heading('name', text='姓名', anchor='center')
        self.participant_tree.heading('whitelist', text='白名单', anchor='center')
        self.participant_tree.column('id', width=50, anchor='center')
        self.participant_tree.column('name', width=150, anchor='center')
        self.participant_tree.column('whitelist', width=80, anchor='center')
        self.participant_tree.pack(side='left', fill='both', expand=True)
        
        # 参与者列表滚动条
        p_scrollbar = ttk.Scrollbar(participants_frame, orient="vertical", command=self.participant_tree.yview)
        p_scrollbar.pack(side='right', fill='y')
        self.participant_tree.configure(yscrollcommand=p_scrollbar.set)
        
        # 参与者操作框架
        participant_ops_frame = ttk.Frame(right_frame)
        participant_ops_frame.pack(fill='x', padx=5, pady=5)
        
        # 参与者名称输入
        ttk.Label(participant_ops_frame, text="参与者姓名:").pack(side='left', padx=5)
        self.participant_name_var = tk.StringVar()
        self.participant_entry = ttk.Entry(participant_ops_frame, textvariable=self.participant_name_var)
        self.participant_entry.pack(side='left', padx=5)
        
        # 白名单复选框
        self.is_whitelist_var = tk.BooleanVar()
        ttk.Checkbutton(participant_ops_frame, text="白名单", variable=self.is_whitelist_var).pack(side='left', padx=5)
        
        # 参与者操作按钮
        ttk.Button(participant_ops_frame, text="添加参与者", command=self.add_participant).pack(side='left', padx=5)
        ttk.Button(participant_ops_frame, text="删除参与者", command=self.delete_participant).pack(side='left', padx=5)
        ttk.Button(participant_ops_frame, text="修改白名单", command=self.toggle_whitelist).pack(side='left', padx=5)
        
        # 导入导出按钮
        io_frame = ttk.Frame(right_frame)
        io_frame.pack(fill='x', padx=5, pady=5)
        ttk.Button(io_frame, text="导入参与者", command=self.import_participants).pack(side='left', padx=5)
        ttk.Button(io_frame, text="导出参与者", command=self.export_participants).pack(side='left', padx=5)
        
        # 绑定选择事件
        self.pool_tree.bind('<<TreeviewSelect>>', self.on_pool_selected)
        
        # 初始化奖池列表
        self.refresh_pools()

    def refresh_pools(self):
        """刷新奖池列表"""
        # 清空奖池列表
        for item in self.pool_tree.get_children():
            self.pool_tree.delete(item)
            
        # 查询所有奖池
        self.cursor.execute('''
            SELECT p.id, p.name, COUNT(pt.id)
            FROM pools p
            LEFT JOIN participants pt ON p.id = pt.pool_id
            GROUP BY p.id, p.name
        ''')
        pools = self.cursor.fetchall()
        
        # 显示奖池列表
        for pool in pools:
            self.pool_tree.insert('', 'end', values=pool)
            
    def refresh_participants(self, pool_id):
        """刷新参与者列表"""
        # 清空参与者列表
        for item in self.participant_tree.get_children():
            self.participant_tree.delete(item)
            
        if not pool_id:
            return
            
        # 查询选中奖池的参与者
        self.cursor.execute('''
            SELECT id, name, is_whitelist
            FROM participants
            WHERE pool_id = ?
        ''', (pool_id,))
        participants = self.cursor.fetchall()
        
        # 显示参与者列表
        for p in participants:
            self.participant_tree.insert('', 'end', values=(p[0], p[1], "是" if p[2] else "否"))
            
    def on_pool_selected(self, event):
        """处理奖池选择事件"""
        # 获取选中的奖池
        selection = self.pool_tree.selection()
        if not selection:
            return
            
        # 获取奖池信息
        pool = self.pool_tree.item(selection[0])
        pool_id = pool['values'][0]
        pool_name = pool['values'][1]
        
        # 更新奖池名称输入框
        self.pool_name_var.set(pool_name)
        
        # 刷新参与者列表
        self.refresh_participants(pool_id)
        
    def add_pool(self):
        """添加新奖池"""
        name = self.pool_name_var.get().strip()
        if not name:
            messagebox.showwarning("警告", "请输入奖池名称")
            return
            
        try:
            self.cursor.execute("INSERT INTO pools (name) VALUES (?)", (name,))
            self.conn.commit()
            self.refresh_pools()
            self.pool_name_var.set("")
            messagebox.showinfo("成功", "添加奖池成功")
        except sqlite3.IntegrityError:
            messagebox.showerror("错误", "奖池名称已存在")
        except Exception as e:
            messagebox.showerror("错误", f"添加奖池失败: {str(e)}")
            
    def delete_pool(self):
        """删除选中的奖池"""
        selection = self.pool_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择要删除的奖池")
            return
            
        if not messagebox.askyesno("确认", "确定要删除选中的奖池吗？这将同时删除奖池中的所有参与者！"):
            return
            
        try:
            pool_id = self.pool_tree.item(selection[0])['values'][0]
            self.cursor.execute("DELETE FROM participants WHERE pool_id = ?", (pool_id,))
            self.cursor.execute("DELETE FROM pools WHERE id = ?", (pool_id,))
            self.conn.commit()
            self.refresh_pools()
            self.refresh_participants(None)
            messagebox.showinfo("成功", "删除奖池成功")
        except Exception as e:
            messagebox.showerror("错误", f"删除奖池失败: {str(e)}")
            
    def rename_pool(self):
        """重命名选中的奖池"""
        selection = self.pool_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择要重命名的奖池")
            return
            
        new_name = self.pool_name_var.get().strip()
        if not new_name:
            messagebox.showwarning("警告", "请输入新的奖池名称")
            return
            
        try:
            pool_id = self.pool_tree.item(selection[0])['values'][0]
            self.cursor.execute("UPDATE pools SET name = ? WHERE id = ?", (new_name, pool_id))
            self.conn.commit()
            self.refresh_pools()
            messagebox.showinfo("成功", "重命名奖池成功")
        except sqlite3.IntegrityError:
            messagebox.showerror("错误", "奖池名称已存在")
        except Exception as e:
            messagebox.showerror("错误", f"重命名奖池失败: {str(e)}")
            
    def add_participant(self):
        """添加新参与者"""
        selection = self.pool_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择奖池")
            return
            
        name = self.participant_name_var.get().strip()
        if not name:
            messagebox.showwarning("警告", "请输入参与者姓名")
            return
            
        try:
            pool_id = self.pool_tree.item(selection[0])['values'][0]
            is_whitelist = self.is_whitelist_var.get()
            
            self.cursor.execute(
                "INSERT INTO participants (name, pool_id, is_whitelist) VALUES (?, ?, ?)",
                (name, pool_id, is_whitelist)
            )
            self.conn.commit()
            
            self.refresh_pools()
            self.refresh_participants(pool_id)
            self.participant_name_var.set("")
            self.is_whitelist_var.set(False)
            messagebox.showinfo("成功", "添加参与者成功")
        except Exception as e:
            messagebox.showerror("错误", f"添加参与者失败: {str(e)}")
            
    def delete_participant(self):
        """删除选中的参与者"""
        pool_selection = self.pool_tree.selection()
        participant_selection = self.participant_tree.selection()
        
        if not pool_selection or not participant_selection:
            messagebox.showwarning("警告", "请选择要删除的参与者")
            return
            
        if not messagebox.askyesno("确认", "确定要删除选中的参与者吗？"):
            return
            
        try:
            pool_id = self.pool_tree.item(pool_selection[0])['values'][0]
            participant_id = self.participant_tree.item(participant_selection[0])['values'][0]
            
            self.cursor.execute("DELETE FROM participants WHERE id = ?", (participant_id,))
            self.conn.commit()
            
            self.refresh_pools()
            self.refresh_participants(pool_id)
            messagebox.showinfo("成功", "删除参与者成功")
        except Exception as e:
            messagebox.showerror("错误", f"删除参与者失败: {str(e)}")
            
    def toggle_whitelist(self):
        """切换参与者的白名单状态"""
        pool_selection = self.pool_tree.selection()
        participant_selection = self.participant_tree.selection()
        
        if not pool_selection or not participant_selection:
            messagebox.showwarning("警告", "请选择要修改的参与者")
            return
            
        try:
            pool_id = self.pool_tree.item(pool_selection[0])['values'][0]
            participant_id = self.participant_tree.item(participant_selection[0])['values'][0]
            
            # 切换白名单状态
            self.cursor.execute(
                "UPDATE participants SET is_whitelist = NOT is_whitelist WHERE id = ?",
                (participant_id,)
            )
            self.conn.commit()
            
            self.refresh_participants(pool_id)
            messagebox.showinfo("成功", "修改白名单状态成功")
        except Exception as e:
            messagebox.showerror("错误", f"修改白名单状态失败: {str(e)}")
            
    def import_participants(self):
        """从文件导入参与者"""
        selection = self.pool_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择奖池")
            return
            
        file_path = filedialog.askopenfilename(
            title="选择文件",
            filetypes=[
                ("CSV Files", "*.csv"),
                ("Word Files", "*.docx")
            ]
        )
        
        if not file_path:
            return
            
        try:
            pool_id = self.pool_tree.item(selection[0])['values'][0]
            names = []
            
            if file_path.endswith('.csv'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    for row in reader:
                        if row and row[0].strip():
                            names.append((row[0].strip(), pool_id, False))
            else:
                doc = Document(file_path)
                for paragraph in doc.paragraphs:
                    if paragraph.text.strip():
                        names.append((paragraph.text.strip(), pool_id, False))
                        
            if names:
                self.cursor.executemany(
                    "INSERT INTO participants (name, pool_id, is_whitelist) VALUES (?, ?, ?)",
                    names
                )
                self.conn.commit()
                
                self.refresh_pools()
                self.refresh_participants(pool_id)
                messagebox.showinfo("成功", f"成功导入 {len(names)} 个参与者")
            else:
                messagebox.showwarning("警告", "文件中没有找到有效的参与者数据")
                
        except Exception as e:
            messagebox.showerror("错误", f"导入参与者失败: {str(e)}")
            
    def export_participants(self):
        """导出参与者列表到文件"""
        selection = self.pool_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择奖池")
            return
            
        pool_id = self.pool_tree.item(selection[0])['values'][0]
        pool_name = self.pool_tree.item(selection[0])['values'][1]
        
        file_path = filedialog.asksaveasfilename(
            title="保存文件",
            defaultextension=".csv",
            initialfile=f"{pool_name}_参与者列表",
            filetypes=[("CSV Files", "*.csv")]
        )
        
        if not file_path:
            return
            
        try:
            self.cursor.execute(
                "SELECT name, is_whitelist FROM participants WHERE pool_id = ?",
                (pool_id,)
            )
            participants = self.cursor.fetchall()
            
            with open(file_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["姓名", "是否白名单"])
                for p in participants:
                    writer.writerow([p[0], "是" if p[1] else "否"])
                    
            messagebox.showinfo("成功", "导出参与者列表成功")
            
        except Exception as e:
            messagebox.showerror("错误", f"导出参与者列表失败: {str(e)}")

    def start_lottery(self):
        if self.is_rolling:
            return
            
        pool_index = self.pool_combo.current()
        count = int(self.count_spin.get())
        
        if pool_index == -1:
            messagebox.showwarning("警告", "请选择抽奖池")
            return
            
        try:
            # 获取奖池ID
            self.cursor.execute('''
                SELECT p.id
                FROM pools p
                ORDER BY p.id
                LIMIT 1 OFFSET ?
            ''', (pool_index,))
            pool_id = self.cursor.fetchone()[0]
            
            # 获取所有参与者，包括白名单
            self.cursor.execute(
                "SELECT name, is_whitelist FROM participants WHERE pool_id = ?",
                (pool_id,)
            )
            participants = self.cursor.fetchall()
            
            if not participants:
                messagebox.showwarning("警告", "该奖池没有参与者")
                return
                
            # 切换到抽奖动画页面
            self.show_lottery()
            
            # 开始抽奖动画
            self.is_rolling = True
            self.current_names = [p[0] for p in participants]  # 动画显示所有人
            self.current_index = 0
            self.start_btn.config(state='disabled')
            
            # 准备可抽奖的名单（排除白名单）
            available_names = [p[0] for p in participants if not p[1]]
            
            if not available_names:
                messagebox.showwarning("警告", "该奖池所有参与者都是白名单用户")
                self.is_rolling = False
                self.start_btn.config(state='normal')
                self.show_setup()
                return
                
            # 启动滚动线程
            threading.Thread(target=self.roll_names, args=(count, available_names), daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("错误", f"抽奖失败: {str(e)}")
            self.show_setup()
            
    def roll_names(self, count, available_names):
        # 滚动显示名字
        start_time = time.time()
        duration = 3  # 滚动持续时间（秒）
        
        while time.time() - start_time < duration:
            self.current_index = (self.current_index + 1) % len(self.current_names)
            self.rolling_label.config(text=self.current_names[self.current_index])
            time.sleep(0.1)
            
        # 从可抽奖名单中随机抽取
        winners = random.sample(available_names, min(count, len(available_names)))
        
        # 清空之前的结果
        self.result_text.delete('1.0', tk.END)
        
        # 显示结果
        for i, winner in enumerate(winners, 1):
            self.result_text.insert(tk.END, f"{i}. {winner}\n")
        
        # 切换到结果页面
        self.show_result()
        
        # 重置状态
        self.is_rolling = False
        self.start_btn.config(state='normal')
            
    def on_tab_changed(self, event):
        # 获取当前选中的标签页
        current_tab = self.notebook.select()
        if current_tab:
            tab_text = self.notebook.tab(current_tab, "text")
            if tab_text == "管理" and not self.is_logged_in:
                # 如果点击的是管理标签且未登录，显示登录窗口
                self.notebook.select(0)  # 切回抽奖标签
                LoginWindow(self)
            elif tab_text == "抽奖":
                # 切换到抽奖标签时刷新数据
                self.refresh_lottery_pools()
            
    def on_closing(self):
        # 关闭窗口时重置登录状态
        self.is_logged_in = False
        self.root.destroy()

    def __del__(self):
        self.conn.close()

if __name__ == '__main__':
    root = tk.Tk()
    app = LotterySystem(root)
    root.mainloop() 