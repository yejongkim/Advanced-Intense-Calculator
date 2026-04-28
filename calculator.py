"""Advanced Intense Calculator — PyQt6 calculator application."""

import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QGridLayout,
    QPushButton, QLabel, QVBoxLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


MAX_DIGITS = 15
MAX_VALUE = 9.999999999999999e99

_STYLESHEET = '''
    QWidget {
        background-color: #000000;
    }
    QLabel#display {
        color: white;
        background-color: #000000;
        padding-right: 8px;
        padding-bottom: 8px;
    }
    QPushButton[btnType="func"] {
        background-color: #a5a5a5;
        color: black;
        border-radius: 40px;
        font-size: 28px;
        font-weight: 400;
    }
    QPushButton[btnType="func"]:pressed {
        background-color: #d9d9d9;
    }
    QPushButton[btnType="op"] {
        background-color: #f1a33c;
        color: white;
        border-radius: 40px;
        font-size: 36px;
        font-weight: 300;
    }
    QPushButton[btnType="op"]:pressed {
        background-color: #fdd49a;
        color: #f1a33c;
    }
    QPushButton[btnType="op_active"] {
        background-color: white;
        color: #f1a33c;
        border-radius: 40px;
        font-size: 36px;
        font-weight: 300;
    }
    QPushButton[btnType="op_active"]:pressed {
        background-color: #f1a33c;
        color: white;
    }
    QPushButton[btnType="num"] {
        background-color: #333333;
        color: white;
        border-radius: 40px;
        font-size: 32px;
        font-weight: 400;
    }
    QPushButton[btnType="num"]:pressed {
        background-color: #737373;
    }
    QPushButton#btn_zero {
        border-radius: 40px;
        text-align: left;
        padding-left: 30px;
    }
'''

_BTN_SIZE = 80
_BTN_GAP = 10
_MARGIN = 15


class Calculator:
    """Core calculator engine handling all arithmetic operations."""

    def __init__(self):
        self._current_input = '0'
        self._previous_input = None
        self._operator = None
        self._should_reset_input = False
        self._has_decimal = False

    @property
    def current_input(self):
        return self._current_input

    @property
    def operator(self):
        return self._operator

    def input_digit(self, digit):
        """Append a digit to the current input."""
        digit_count = len(
            self._current_input.replace('-', '').replace('.', '')
        )
        if self._should_reset_input:
            self._current_input = digit
            self._should_reset_input = False
            self._has_decimal = False
        elif self._current_input == '0':
            self._current_input = digit
        elif digit_count < MAX_DIGITS:
            self._current_input += digit

    def input_decimal(self):
        """Add a decimal point if not already present."""
        if self._should_reset_input:
            self._current_input = '0.'
            self._should_reset_input = False
            self._has_decimal = True
            return
        if not self._has_decimal:
            self._current_input += '.'
            self._has_decimal = True

    def reset(self):
        """Reset all calculator state (AC)."""
        self._current_input = '0'
        self._previous_input = None
        self._operator = None
        self._should_reset_input = False
        self._has_decimal = False

    def clear_entry(self):
        """Clear only the current entry (C), preserving any pending operator."""
        self._current_input = '0'
        self._has_decimal = False

    def negative_positive(self):
        """Toggle the sign of the current value (+/-)."""
        if self._current_input in ('0', 'Error', 'Overflow'):
            return
        if self._current_input.startswith('-'):
            self._current_input = self._current_input[1:]
        else:
            self._current_input = '-' + self._current_input

    def percent(self):
        """Divide the current value by 100 (%)."""
        if self._current_input in ('Error', 'Overflow'):
            return
        try:
            value = float(self._current_input) / 100
            self._current_input = self._format_number(value)
            self._has_decimal = '.' in self._current_input
        except (ValueError, OverflowError):
            pass

    def set_operator(self, operator):
        """Store the current value and record a pending operator."""
        if self._current_input in ('Error', 'Overflow'):
            return
        if self._operator and self._should_reset_input:
            self._operator = operator
            return
        if self._operator and not self._should_reset_input:
            self.equal()
            if self._current_input in ('Error', 'Overflow'):
                return
        self._previous_input = self._current_input
        self._operator = operator
        self._should_reset_input = True

    def add(self, a, b):
        """Return the sum of a and b."""
        return a + b

    def subtract(self, a, b):
        """Return a minus b."""
        return a - b

    def multiply(self, a, b):
        """Return the product of a and b."""
        return a * b

    def divide(self, a, b):
        """Return a divided by b.

        Raises:
            ZeroDivisionError: If b is zero.
        """
        if b == 0:
            raise ZeroDivisionError('0으로 나눌 수 없습니다.')
        return a / b

    def equal(self):
        """Compute and return the result of the pending operation."""
        if self._operator is None or self._previous_input is None:
            return self._current_input
        if self._current_input in ('Error', 'Overflow'):
            return self._current_input

        try:
            a = float(self._previous_input)
            b = float(self._current_input)

            if self._operator == '+':
                result = self.add(a, b)
            elif self._operator == '-':
                result = self.subtract(a, b)
            elif self._operator == '×':
                result = self.multiply(a, b)
            elif self._operator == '÷':
                result = self.divide(a, b)
            else:
                return self._current_input

            if abs(result) > MAX_VALUE:
                raise OverflowError('처리할 수 있는 숫자의 범위를 초과했습니다.')

            self._current_input = self._format_number(result)
            self._has_decimal = '.' in self._current_input
            self._previous_input = None
            self._operator = None
            self._should_reset_input = True
            return self._current_input

        except ZeroDivisionError:
            self.reset()
            self._current_input = 'Error'
            return 'Error'
        except OverflowError:
            self.reset()
            self._current_input = 'Overflow'
            return 'Overflow'

    def is_error(self):
        """Return True if the calculator is in an error state."""
        return self._current_input in ('Error', 'Overflow')

    def _format_number(self, value):
        """Format a float for display, rounding to at most 6 decimal places."""
        if value != value:  # NaN guard
            return 'Error'

        abs_val = abs(value)

        if abs_val >= 1e15 or (0 < abs_val < 1e-6):
            return f'{value:.6e}'

        if value == int(value):
            return str(int(value))

        rounded = round(value, 6)
        if rounded == int(rounded):
            return str(int(rounded))

        return f'{rounded:.6f}'.rstrip('0').rstrip('.')


class CalculatorWindow(QWidget):
    """PyQt6 iOS-style calculator UI."""

    def __init__(self):
        super().__init__()
        self._calc = Calculator()
        self._op_buttons = {}
        self._ac_btn = None
        self._display = None
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle('Calculator')
        width = 4 * _BTN_SIZE + 3 * _BTN_GAP + 2 * _MARGIN
        height = 200 + 5 * _BTN_SIZE + 4 * _BTN_GAP + 2 * _MARGIN + 10
        self.setFixedSize(width, height)
        self.setStyleSheet(_STYLESHEET)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(_MARGIN, _MARGIN, _MARGIN, _MARGIN)
        main_layout.setSpacing(0)

        self._display = QLabel('0')
        self._display.setObjectName('display')
        self._display.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom
        )
        self._display.setFixedHeight(200)
        self._display.setWordWrap(False)
        self._adjust_font('0')
        main_layout.addWidget(self._display)

        grid = QGridLayout()
        grid.setSpacing(_BTN_GAP)
        grid.setContentsMargins(0, 0, 0, 0)

        self._ac_btn = self._make_btn('AC', 'func')
        self._ac_btn.clicked.connect(self._on_ac)
        grid.addWidget(self._ac_btn, 0, 0)

        neg_pos_btn = self._make_btn('+/-', 'func')
        neg_pos_btn.clicked.connect(self._on_neg_pos)
        grid.addWidget(neg_pos_btn, 0, 1)

        pct_btn = self._make_btn('%', 'func')
        pct_btn.clicked.connect(self._on_percent)
        grid.addWidget(pct_btn, 0, 2)

        div_btn = self._make_btn('÷', 'op')
        div_btn.clicked.connect(lambda: self._on_operator('÷'))
        grid.addWidget(div_btn, 0, 3)
        self._op_buttons['÷'] = div_btn

        for col, digit in enumerate(['7', '8', '9']):
            btn = self._make_btn(digit, 'num')
            btn.clicked.connect(lambda _, d=digit: self._on_digit(d))
            grid.addWidget(btn, 1, col)
        mul_btn = self._make_btn('×', 'op')
        mul_btn.clicked.connect(lambda: self._on_operator('×'))
        grid.addWidget(mul_btn, 1, 3)
        self._op_buttons['×'] = mul_btn

        for col, digit in enumerate(['4', '5', '6']):
            btn = self._make_btn(digit, 'num')
            btn.clicked.connect(lambda _, d=digit: self._on_digit(d))
            grid.addWidget(btn, 2, col)
        sub_btn = self._make_btn('−', 'op')
        sub_btn.clicked.connect(lambda: self._on_operator('-'))
        grid.addWidget(sub_btn, 2, 3)
        self._op_buttons['-'] = sub_btn

        for col, digit in enumerate(['1', '2', '3']):
            btn = self._make_btn(digit, 'num')
            btn.clicked.connect(lambda _, d=digit: self._on_digit(d))
            grid.addWidget(btn, 3, col)
        add_btn = self._make_btn('+', 'op')
        add_btn.clicked.connect(lambda: self._on_operator('+'))
        grid.addWidget(add_btn, 3, 3)
        self._op_buttons['+'] = add_btn

        zero_btn = self._make_btn('0', 'num', wide=True)
        zero_btn.setObjectName('btn_zero')
        zero_btn.clicked.connect(lambda: self._on_digit('0'))
        grid.addWidget(zero_btn, 4, 0, 1, 2)

        dot_btn = self._make_btn('.', 'num')
        dot_btn.clicked.connect(self._on_decimal)
        grid.addWidget(dot_btn, 4, 2)

        eq_btn = self._make_btn('=', 'op')
        eq_btn.clicked.connect(self._on_equal)
        grid.addWidget(eq_btn, 4, 3)

        main_layout.addLayout(grid)

    def _make_btn(self, text, btn_type, wide=False):
        btn = QPushButton(text)
        btn.setFixedHeight(_BTN_SIZE)
        if wide:
            btn.setFixedWidth(2 * _BTN_SIZE + _BTN_GAP)
        else:
            btn.setFixedWidth(_BTN_SIZE)
        btn.setProperty('btnType', btn_type)
        return btn

    def _refresh_btn_style(self, btn):
        btn.style().unpolish(btn)
        btn.style().polish(btn)
        btn.update()

    def _set_active_op(self, operator):
        for op, btn in self._op_buttons.items():
            new_type = 'op_active' if op == operator else 'op'
            btn.setProperty('btnType', new_type)
            self._refresh_btn_style(btn)

    def _clear_active_op(self):
        for btn in self._op_buttons.values():
            btn.setProperty('btnType', 'op')
            self._refresh_btn_style(btn)

    def _adjust_font(self, text):
        """Resize display font based on text length (bonus requirement)."""
        length = len(text)
        if length <= 6:
            size = 88
        elif length <= 9:
            size = 70
        elif length <= 12:
            size = 52
        else:
            size = 38
        self._display.setFont(
            QFont('Helvetica Neue', size, QFont.Weight.Light)
        )

    def _refresh_display(self):
        text = self._calc.current_input
        self._display.setText(text)
        self._adjust_font(text)

    def _on_digit(self, digit):
        if self._calc.is_error():
            return
        self._calc.input_digit(digit)
        self._ac_btn.setText('C')
        self._clear_active_op()
        self._refresh_display()

    def _on_decimal(self):
        if self._calc.is_error():
            return
        self._calc.input_decimal()
        self._ac_btn.setText('C')
        self._clear_active_op()
        self._refresh_display()

    def _on_ac(self):
        if self._ac_btn.text() == 'C':
            self._calc.clear_entry()
        else:
            self._calc.reset()
            self._clear_active_op()
        self._ac_btn.setText('AC')
        self._refresh_display()

    def _on_neg_pos(self):
        self._calc.negative_positive()
        self._refresh_display()

    def _on_percent(self):
        self._calc.percent()
        self._refresh_display()

    def _on_operator(self, operator):
        if self._calc.is_error():
            return
        self._calc.set_operator(operator)
        self._set_active_op(operator)
        self._refresh_display()

    def _on_equal(self):
        self._calc.equal()
        self._ac_btn.setText('C')
        self._clear_active_op()
        self._refresh_display()


def main():
    app = QApplication(sys.argv)
    window = CalculatorWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
