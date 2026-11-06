"""Persian-friendly desktop phone number inspector."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from phone_inspector import PhoneInputError, inspect_number


BG = "#f4f7fb"
CARD = "#ffffff"
INK = "#172b4d"
MUTED = "#63738a"
ACCENT = "#176b87"


class PhoneInspectorApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("بررسی شماره تلفن")
        self.root.geometry("760x760")
        self.root.minsize(620, 680)
        self.root.configure(bg=BG)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TCombobox", padding=7, fieldbackground=CARD)
        style.configure(
            "Primary.TButton",
            padding=(18, 10),
            background=ACCENT,
            foreground="white",
            font=("Segoe UI", 10, "bold"),
        )
        style.map("Primary.TButton", background=[("active", "#10546b")])
        style.configure("Secondary.TButton", padding=(14, 9))

        self.number_var = tk.StringVar()
        self.region_var = tk.StringVar(value="ایران (+98)")
        self.status_var = tk.StringVar(value="شماره را وارد کنید و بررسی را بزنید.")
        self.result_vars: dict[str, tk.StringVar] = {}

        self._build_ui()
        self.root.bind("<Return>", lambda _event: self.analyze())
        self.root.bind("<Control-l>", lambda _event: self.clear())
        self.number_entry.focus_set()

    def _label(
        self, parent: tk.Widget, text: str, *, size: int = 10, color: str = INK, bold: bool = False
    ) -> tk.Label:
        return tk.Label(
            parent,
            text=text,
            bg=parent.cget("bg"),
            fg=color,
            font=("Segoe UI", size, "bold" if bold else "normal"),
            anchor="e",
            justify="right",
        )

    def _build_ui(self) -> None:
        page = tk.Frame(self.root, bg=BG, padx=30, pady=24)
        page.pack(fill="both", expand=True)

        self._label(page, "بررسی‌گر شماره تلفن", size=22, color=INK, bold=True).pack(
            anchor="e"
        )
        self._label(
            page,
            "اعتبارسنجی و نمایش اطلاعات طرح شماره‌گذاری، به‌صورت کاملاً محلی",
            color=MUTED,
        ).pack(anchor="e", pady=(4, 18))

        form = tk.Frame(page, bg=CARD, padx=20, pady=18, highlightbackground="#e2e9f1", highlightthickness=1)
        form.pack(fill="x")
        self._label(form, "شماره تلفن", bold=True).pack(anchor="e")
        self.number_entry = tk.Entry(
            form,
            textvariable=self.number_var,
            justify="right",
            font=("Segoe UI", 14),
            relief="solid",
            bd=1,
            highlightthickness=2,
            highlightbackground="#d9e2ec",
            highlightcolor=ACCENT,
        )
        self.number_entry.pack(fill="x", ipady=8, pady=(7, 12))
        self.number_entry.bind("<Return>", lambda _event: self.analyze())

        self._label(form, "کشور پیش‌فرض برای شماره‌های بدون کد کشور").pack(anchor="e")
        self.region_box = ttk.Combobox(
            form,
            textvariable=self.region_var,
            values=("ایران (+98)", "ایالات متحده (+1)", "بریتانیا (+44)", "آلمان (+49)", "فرانسه (+33)", "ترکیه (+90)"),
            state="readonly",
            justify="right",
        )
        self.region_box.pack(fill="x", pady=(6, 14))

        actions = tk.Frame(form, bg=CARD)
        actions.pack(fill="x")
        ttk.Button(actions, text="بررسی شماره", style="Primary.TButton", command=self.analyze).pack(
            side="right"
        )
        ttk.Button(actions, text="پاک کردن", style="Secondary.TButton", command=self.clear).pack(
            side="right", padx=(0, 8)
        )

        self.status_label = self._label(page, self.status_var.get(), color=MUTED)
        self.status_label.pack(anchor="e", pady=(12, 8))

        result_card = tk.Frame(page, bg=CARD, padx=20, pady=16, highlightbackground="#e2e9f1", highlightthickness=1)
        result_card.pack(fill="both", expand=True)
        self._label(result_card, "نتیجه بررسی", size=13, bold=True).pack(anchor="e", pady=(0, 8))

        rows = (
            ("اعتبار شماره", "validity"),
            ("امکان‌پذیری طول شماره", "possible"),
            ("کشور / منطقه احتمالی", "region"),
            ("کد کشور", "calling_code"),
            ("نوع خط", "number_type"),
            ("منطقه زمانی احتمالی", "time_zones"),
            ("اپراتور (در صورت وجود)", "carrier"),
            ("قالب بین‌المللی", "international"),
            ("قالب ملی", "national"),
            ("قالب استاندارد E.164", "e164"),
        )
        for title, key in rows:
            row = tk.Frame(result_card, bg=CARD, pady=5)
            row.pack(fill="x")
            value = tk.StringVar(value="—")
            self.result_vars[key] = value
            tk.Label(
                row,
                textvariable=value,
                bg=CARD,
                fg=INK,
                font=("Segoe UI", 10, "bold"),
                anchor="w",
                justify="left",
                wraplength=390,
            ).pack(side="left", fill="x", expand=True)
            self._label(row, title, color=MUTED).pack(side="right", padx=(10, 0))

        self.copy_button = ttk.Button(
            result_card, text="کپی شماره استاندارد", style="Secondary.TButton", command=self.copy_number, state="disabled"
        )
        self.copy_button.pack(anchor="e", pady=(12, 0))
        self._label(
            page,
            "اطلاعات اپراتور و منطقه از پایگاه شماره‌گذاری استخراج می‌شوند؛ مکان دقیق، هویت مشترک و وضعیت فعال‌بودن سیم‌کارت قابل تشخیص نیست.",
            size=9,
            color=MUTED,
        ).pack(anchor="e", pady=(12, 0))

    def analyze(self) -> None:
        try:
            region = {
                "ایران (+98)": "IR",
                "ایالات متحده (+1)": "US",
                "بریتانیا (+44)": "GB",
                "آلمان (+49)": "DE",
                "فرانسه (+33)": "FR",
                "ترکیه (+90)": "TR",
            }[self.region_var.get()]
            details = inspect_number(self.number_var.get(), region)
        except PhoneInputError as error:
            self._reset_results()
            self._set_status(str(error), error=True)
            return

        values = {
            "validity": "معتبر" if details.valid else "نامعتبر بر اساس طرح شماره‌گذاری",
            "possible": "طول قابل‌قبول" if details.possible else "طول ناممکن",
            "region": f"{details.region_name} ({details.region_code})",
            "calling_code": details.country_calling_code,
            "number_type": details.number_type,
            "time_zones": "، ".join(details.time_zones) if details.time_zones else "در دسترس نیست",
            "carrier": details.carrier_name,
            "international": details.international,
            "national": details.national,
            "e164": details.e164,
        }
        for key, value in values.items():
            self.result_vars[key].set(value)
        self.copy_button.configure(state="normal")
        if details.valid:
            self._set_status("بررسی انجام شد. معتبر بودن به معنی فعال بودن شماره نیست.", success=True)
        elif details.possible:
            self._set_status("طول شماره ممکن است، اما الگوی آن در طرح شماره‌گذاری معتبر نیست.", warning=True)
        else:
            self._set_status("این شماره با طرح شماره‌گذاری انتخاب‌شده سازگار نیست.", error=True)

    def _reset_results(self) -> None:
        for value in self.result_vars.values():
            value.set("—")
        self.copy_button.configure(state="disabled")

    def _set_status(
        self, message: str, *, error: bool = False, warning: bool = False, success: bool = False
    ) -> None:
        color = "#a62e2e" if error else "#9a6500" if warning else "#19734a" if success else MUTED
        self.status_var.set(message)
        self.status_label.configure(text=message, fg=color)

    def copy_number(self) -> None:
        value = self.result_vars["e164"].get()
        if value == "—":
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(value)
        self._set_status("شماره استاندارد در کلیپ‌بورد کپی شد.", success=True)

    def clear(self) -> None:
        self.number_var.set("")
        self.region_var.set("ایران (+98)")
        self._reset_results()
        self._set_status("شماره را وارد کنید و بررسی را بزنید.")
        self.number_entry.focus_set()


def main() -> None:
    root = tk.Tk()
    PhoneInspectorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
