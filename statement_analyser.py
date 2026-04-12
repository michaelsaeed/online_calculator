import streamlit as st
import pdfplumber
import pandas as pd
import re
import io
from collections import defaultdict
from datetime import date, datetime

st.set_page_config(page_title="Covered Call Analyser", page_icon="📈", layout="wide")
st.markdown("""
<style>
details summary p { font-size: 1.1rem !important; font-weight: 600 !important; }
</style>
""", unsafe_allow_html=True)
st.title("📈 Covered Call Statement Analyser")

# ── PDF EXTRACTION ─────────────────────────────────────────────────────────────

def extract_text(uploaded_file):
    pages = []
    with pdfplumber.open(io.BytesIO(uploaded_file.read())) as pdf:
        for page in pdf.pages:
            t = page.extract_text(x_tolerance=2, y_tolerance=2)
            if t:
                pages.append(t)
    return "\n".join(pages)

def to_float(s):
    try:
        return float(str(s).replace(",", "").strip())
    except (ValueError, AttributeError):
        return None

def parse_period(text):
    m = re.search(r'Activity Statement\s*[-–]\s*(\w+ \d+, \d{4})\s*[-–]\s*(\w+ \d+, \d{4})', text)
    if m:
        return f"{m.group(1)} – {m.group(2)}"
    m2 = re.search(r'(\w+ \d+, \d{4}).*?(\w+ \d+, \d{4})', text)
    return f"{m2.group(1)} – {m2.group(2)}" if m2 else ""

def days_between(d1_str, d2_str):
    try:
        d1 = datetime.strptime(d1_str, '%Y-%m-%d').date()
        d2 = datetime.strptime(d2_str, '%Y-%m-%d').date()
        return (d2 - d1).days
    except Exception:
        return None

# ── FORMAT DETECTION ──────────────────────────────────────────────────────────

def detect_format(header_line):
    return 'A' if 'C. Price' in header_line else 'B'

# ── TRADES SECTION FINDER ─────────────────────────────────────────────────────

def find_trades_section(text):
    lines = text.split('\n')
    debug = {}
    trades_start = None
    fmt = 'B'

    for i, line in enumerate(lines):
        if line.strip() == 'Trades':
            for j in range(i + 1, min(i + 8, len(lines))):
                hdr = lines[j].strip()
                if 'Symbol' in hdr and 'Quantity' in hdr and 'T. Price' in hdr:
                    trades_start = j + 1
                    fmt = detect_format(hdr)
                    debug['method'] = f'Header at line {j}'
                    break
            if trades_start:
                break

    if trades_start is None:
        for i, line in enumerate(lines):
            if line.strip() == 'Stocks':
                trades_start = i
                debug['method'] = f'"Stocks" at line {i}'
                break

    if trades_start is None:
        debug['error'] = True
        return text, fmt, debug

    end_markers = {
        'Deposits & Withdrawals', 'Fees', 'Financial Instrument Information',
        'Cash Report', 'Open Positions', 'Dividends', 'Interest',
        'Change in Dividend Accruals', 'Withholding Tax', 'Notes/Legal Notes',
    }
    trades_end = len(lines)
    for i in range(trades_start, len(lines)):
        if lines[i].strip() in end_markers:
            trades_end = i
            debug['end_marker'] = lines[i].strip()
            break

    return '\n'.join(lines[trades_start:trades_end]), fmt, debug

# ── TRADE LINE PATTERNS ───────────────────────────────────────────────────────

STOCK_A = re.compile(
    r'^([A-Z]{1,6})\s+(-?[\d,]+)\s+([\d.]+)\s+([\d.]+)\s+(-?[\d,]+\.?\d*)\s+(-?[\d,.]+)\s+(-?[\d,.]+)\s+(-?[\d,.]+)'
)
OPT_A = re.compile(
    r'^([A-Z]{1,6})\s+(\d{2}[A-Z]{3}\d{2})\s+([\d.]+)\s+([CP])\s+(-?[\d,]+)\s+([\d.]+)\s+([\d.]+)\s+(-?[\d,]+\.?\d*)\s+(-?[\d,.]+)\s+(-?[\d,.]+)\s+(-?[\d,.]+)'
)
STOCK_B = re.compile(
    r'^([A-Z]{1,6})\s+(-?[\d,]+)\s+([\d.]+)\s+(-?[\d,]+\.?\d*)\s+(-?[\d,.]+)\s+(-?[\d,.]+)\s+(-?[\d,.]+)'
)
OPT_B = re.compile(
    r'^([A-Z]{1,6})\s+(\d{2}[A-Z]{3}\d{2})\s+([\d.]+)\s+([CP])\s+(-?[\d,]+)\s+([\d.]+)\s+(-?[\d,]+\.?\d*)\s+(-?[\d,.]+)\s+(-?[\d,.]+)\s+(-?[\d,.]+)'
)
HEADER_RE = re.compile(r'^Symbol\s+Date')

def parse_trades(section_text, fmt):
    result = defaultdict(lambda: {'stock_trades': [], 'option_trades': []})
    current_type = 'stock'
    current_date = ''
    stock_re = STOCK_A if fmt == 'A' else STOCK_B
    opt_re   = OPT_A   if fmt == 'A' else OPT_B

    skip_prefixes = ('Forex', 'Total', 'USD', 'AUD', 'EUR', 'GBP',
                     'Activity', 'Deposits', 'Fees', 'Financial', 'Cash',
                     'Note', 'Mark', 'Realized', 'Open Pos', 'Symbol')

    for line in section_text.split('\n'):
        ls = line.strip()
        if not ls:
            continue
        if ls == 'Stocks':
            current_type = 'stock'; continue
        if 'Equity and Index Options' in ls:
            current_type = 'option'; continue
        date_m = re.match(r'^(\d{4}-\d{2}-\d{2}),$', ls)
        if date_m:
            current_date = date_m.group(1); continue
        if re.match(r'^\d{2}:\d{2}:\d{2}$', ls):
            continue
        if HEADER_RE.match(ls):
            fmt_new = detect_format(ls)
            if fmt_new != fmt:
                fmt = fmt_new
                stock_re = STOCK_A if fmt == 'A' else STOCK_B
                opt_re   = OPT_A   if fmt == 'A' else OPT_B
            continue
        if any(ls.startswith(p) for p in skip_prefixes):
            continue
        if ls in ('Deposits & Withdrawals', 'Fees', 'Financial Instrument Information',
                  'Cash Report', 'Open Positions', 'Interest'):
            break

        if current_type == 'stock':
            m = stock_re.match(ls)
            if m:
                if fmt == 'A':
                    result[m.group(1)]['stock_trades'].append({
                        'date': current_date, 'qty': to_float(m.group(2)),
                        't_price': to_float(m.group(3)), 'c_price': to_float(m.group(4)),
                        'comm': to_float(m.group(6)), 'realized': to_float(m.group(8)),
                    })
                else:
                    result[m.group(1)]['stock_trades'].append({
                        'date': current_date, 'qty': to_float(m.group(2)),
                        't_price': to_float(m.group(3)), 'c_price': None,
                        'comm': to_float(m.group(5)), 'realized': to_float(m.group(7)),
                    })
        elif current_type == 'option':
            m = opt_re.match(ls)
            if m:
                if fmt == 'A':
                    result[m.group(1)]['option_trades'].append({
                        'date': current_date, 'expiry': m.group(2),
                        'strike': to_float(m.group(3)), 'cp': m.group(4),
                        'qty': to_float(m.group(5)), 't_price': to_float(m.group(6)),
                        'c_price': to_float(m.group(7)), 'comm': to_float(m.group(9)),
                        'realized': to_float(m.group(11)),
                    })
                else:
                    result[m.group(1)]['option_trades'].append({
                        'date': current_date, 'expiry': m.group(2),
                        'strike': to_float(m.group(3)), 'cp': m.group(4),
                        'qty': to_float(m.group(5)), 't_price': to_float(m.group(6)),
                        'c_price': None, 'comm': to_float(m.group(8)),
                        'realized': to_float(m.group(10)),
                    })

    return dict(result)

# ── CYCLE BUILDER ─────────────────────────────────────────────────────────────

def merge_same_day_trades(trades_list):
    """Merge multiple buy (or sell) trades on the same date into one combined trade."""
    by_date = defaultdict(lambda: {'qty': 0, 't_price_total': 0, 'date': ''})
    for t in trades_list:
        d = t.get('date', '')
        by_date[d]['qty'] += (t['qty'] or 0)
        # Weighted average price
        by_date[d]['t_price_total'] += (t['qty'] or 0) * (t['t_price'] or 0)
        by_date[d]['date'] = d
    merged = []
    for d, v in sorted(by_date.items()):
        if v['qty'] != 0:
            avg_price = abs(v['t_price_total'] / v['qty']) if v['qty'] else 0
            merged.append({'date': d, 'qty': v['qty'], 't_price': avg_price, 'c_price': None, 'comm': 0, 'realized': 0})
    return merged

def build_cycles(sym, trades):
    stock = sorted(trades.get('stock_trades', []), key=lambda t: t.get('date', ''))
    opts  = sorted(trades.get('option_trades', []), key=lambda o: o.get('date', ''))
    # Merge buys and sells that occur on the same date into single combined trades
    raw_buys  = [t for t in stock if (t['qty'] or 0) > 0]
    raw_sells = [t for t in stock if (t['qty'] or 0) < 0]
    buys  = merge_same_day_trades(raw_buys)
    sells = merge_same_day_trades(raw_sells)
    cycles = []
    used_opts = set()

    def opt_qty_matches(o, stock_qty):
        """Option contracts must match stock quantity (stock qty 300 = 3 contracts)."""
        return abs(o.get('qty') or 0) == stock_qty / 100

    def opts_in_range(d_start, d_end, stock_qty=None):
        result = []
        for i, o in enumerate(opts):
            if i in used_opts:
                continue
            d = o.get('date', '')
            if (d_start is None or d >= d_start) and (d_end is None or d <= d_end):
                # If stock_qty provided, only include options whose contract qty matches
                if stock_qty is not None and not opt_qty_matches(o, stock_qty):
                    continue
                result.append((i, o))
        return result

    open_buys = list(buys)
    paired_buys = set()

    for sell in sells:
        sell_date = sell.get('date', '')
        candidate = None
        for b in reversed(open_buys):
            if id(b) not in paired_buys and b.get('date', '') <= sell_date:
                candidate = b
                break
        if candidate:
            paired_buys.add(id(candidate))
            buy_date = candidate.get('date', '')
            stock_qty = abs(candidate['qty'] or 1)
            # Options must fall within buy-sell date range AND match stock qty
            cycle_opts_idx = opts_in_range(buy_date, sell_date, stock_qty=stock_qty)
            for i, _ in cycle_opts_idx:
                used_opts.add(i)
            cycles.append({
                'situation': 'exercised',
                'stock': sorted([candidate, sell], key=lambda t: t.get('date', '')),
                'opts': [o for _, o in cycle_opts_idx],
                'buy_price': candidate['t_price'], 'sell_price': sell['t_price'],
                'stock_qty': stock_qty,
                'buy_date': buy_date, 'sell_date': sell.get('date', ''),
            })
        else:
            stock_qty = abs(sell['qty'] or 1)
            cycle_opts_idx = opts_in_range(None, sell_date, stock_qty=stock_qty)
            for i, _ in cycle_opts_idx:
                used_opts.add(i)
            cycles.append({
                'situation': 'sell_only',
                'stock': [sell], 'opts': [o for _, o in cycle_opts_idx],
                'buy_price': None, 'sell_price': sell['t_price'],
                'stock_qty': stock_qty,
                'buy_date': None, 'sell_date': sell.get('date', ''),
            })

    for b in open_buys:
        if id(b) in paired_buys:
            continue
        buy_date = b.get('date', '')
        stock_qty = abs(b['qty'] or 1)
        # Options must start from buy date AND match stock qty
        cycle_opts_idx = [(i, o) for i, o in opts_in_range(buy_date, None, stock_qty=stock_qty) if i not in used_opts]
        for i, _ in cycle_opts_idx:
            used_opts.add(i)
        cycles.append({
            'situation': 'open',
            'stock': [b], 'opts': [o for _, o in cycle_opts_idx],
            'buy_price': b['t_price'], 'sell_price': None,
            'stock_qty': stock_qty,
            'buy_date': buy_date, 'sell_date': None,
        })

    leftover = [(i, o) for i, o in enumerate(opts) if i not in used_opts]
    if leftover:
        cycles.append({
            'situation': 'options_only',
            'stock': [], 'opts': [o for _, o in leftover],
            'buy_price': None, 'sell_price': None, 'stock_qty': 1,
            'buy_date': None, 'sell_date': None,
        })

    return cycles


def calc_cycle(cycle):
    situation  = cycle['situation']
    opts       = cycle['opts']
    stock_qty  = cycle['stock_qty']
    buy_price  = cycle['buy_price']
    sell_price = cycle['sell_price']
    buy_date   = cycle.get('buy_date')
    sell_date  = cycle.get('sell_date')

    opt_premium_net = 0.0
    for o in opts:
        contracts = abs(o['qty'] or 0)
        if (o['qty'] or 0) < 0:
            opt_premium_net += contracts * (o['t_price'] or 0)
        else:
            opt_premium_net -= contracts * (o['t_price'] or 0)

    opt_per_share = opt_premium_net * 100 / stock_qty if stock_qty else 0

    # Days held
    if situation == 'exercised' and buy_date and sell_date:
        days = days_between(buy_date, sell_date)
    elif situation == 'open' and buy_date:
        days = days_between(buy_date, date.today().strftime('%Y-%m-%d'))
    else:
        days = None

    if situation == 'exercised' and buy_price and sell_price:
        be     = buy_price - opt_per_share
        profit = (sell_price - buy_price) + opt_per_share
        roi    = profit / buy_price * 100 if buy_price else None
        ann_roi = (roi / days * 365) if (roi is not None and days and days > 0) else None
    elif situation == 'open' and buy_price:
        be      = buy_price - opt_per_share
        profit  = opt_per_share
        roi     = profit / buy_price * 100 if buy_price else None
        ann_roi = (roi / days * 365) if (roi is not None and days and days > 0) else None
    elif situation == 'sell_only':
        be = profit = roi = ann_roi = None
        opt_pnl = opt_premium_net * 100
        total_pnl = opt_pnl if opt_pnl != 0 else None
        return be, profit, roi, ann_roi, days, total_pnl
    elif situation == 'options_only':
        be = roi = ann_roi = None
        opt_pnl = opt_premium_net * 100
        profit = opt_pnl if opt_pnl != 0 else None
        total_pnl = profit
        return be, profit, roi, ann_roi, days, total_pnl
    else:
        be = profit = roi = ann_roi = None

    total_pnl = profit * stock_qty if profit is not None else None

    return be, profit, roi, ann_roi, days, total_pnl

# ── FORMATTING ────────────────────────────────────────────────────────────────

def fp(v, sign=False, decimals=4):
    if v is None: return '—'
    if sign:
        prefix = '+$' if v >= 0 else '-$'
        return f"{prefix}{abs(v):,.{decimals}f}"
    return f"${v:,.{decimals}f}"

def fq(v):
    if v is None: return '—'
    return f"+{int(v):,}" if v > 0 else f"{int(v):,}"

def fpct(v):
    if v is None: return '—'
    return f"{'+'if v>=0 else ''}{v:.2f}%"

def fdays(v):
    if v is None: return '—'
    return f"{v}d"

# ── PORTFOLIO DASHBOARD ───────────────────────────────────────────────────────

def render_dashboard(trades, period=None):
    all_cycles = []
    for sym, t in trades.items():
        for cycle in build_cycles(sym, t):
            be, profit, roi, ann_roi, days, total_pnl = calc_cycle(cycle)
            all_cycles.append({
                'sym': sym,
                'situation': cycle['situation'],
                'buy_date': cycle.get('buy_date', ''),
                'profit': profit,
                'roi': roi,
                'days': days,
                'total_pnl': total_pnl,
                'stock_qty': cycle.get('stock_qty', 0),
            })

    total_positions = len(all_cycles)
    closed = len([c for c in all_cycles if c['situation'] in ('exercised', 'sell_only')])
    open_pos = len([c for c in all_cycles if c['situation'] in ('open', 'options_only')])
    total_pnl_sum = sum(c['total_pnl'] for c in all_cycles if c['total_pnl'] is not None)

    st.subheader("Portfolio Summary")
    if period:
        st.markdown(f"**Statement Period:** {period}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total P&L",
              f"{'+'if total_pnl_sum>=0 else ''}${total_pnl_sum:,.2f}",
              delta="profit" if total_pnl_sum >= 0 else "loss",
              delta_color="normal" if total_pnl_sum >= 0 else "inverse")
    c2.metric("Total Positions", total_positions)
    c3.metric("Closed Positions", closed)
    c4.metric("Open Positions", open_pos)

    # Per-position summary table — one row per cycle
    rows = []
    for sym, t in sorted(trades.items()):
        for i, cycle in enumerate(build_cycles(sym, t), 1):
            if cycle['situation'] == 'options_only':
                be, profit, roi, ann_roi, days, total_pnl = calc_cycle(cycle)
                cycles_for_sym = build_cycles(sym, t)
                trade_label = f"{sym} — Trade {i}" if len(cycles_for_sym) > 1 else sym
                opt_dates = [o.get('date', '') for o in cycle['opts'] if o.get('date')]
                close_date = max(opt_dates) if opt_dates else '—'
                rows.append({
                    'Position':  trade_label,
                    'Status':    'Options Only',
                    'Date':      close_date,
                    'ROI':       '—',
                    'Total P&L': fp(total_pnl, sign=True, decimals=2) if total_pnl is not None else '—',
                    'Days Held': '—',
                })
                continue
            be, profit, roi, ann_roi, days, total_pnl = calc_cycle(cycle)
            situation_label = {
                'exercised': 'Closed',
                'open':      'Open',
                'sell_only': 'Closed (prior buy)',
            }.get(cycle['situation'], cycle['situation'])
            cycles_for_sym = build_cycles(sym, t)
            trade_label = f"{sym} — Trade {i}" if len(cycles_for_sym) > 1 else sym
            has_options_sold = cycle['situation'] == 'open' and any((o['qty'] or 0) < 0 for o in cycle['opts'])
            rows.append({
                'Position':  trade_label,
                'Status':    'Open (no options sold)' if (cycle['situation'] == 'open' and not has_options_sold) else situation_label,
                'Date':      cycle.get('buy_date') or cycle.get('sell_date') or '—',
                'ROI':       '—' if (cycle['situation'] == 'open' and not has_options_sold) else fpct(roi),
                'Total P&L': '—' if (cycle['situation'] == 'open' and not has_options_sold) else (fp(total_pnl, sign=True, decimals=2) if total_pnl is not None else '—'),
                'Days Held': '—' if cycle['situation'] == 'open' else fdays(days),
            })

    if rows:
        st.markdown("#### Positions")
        st.caption("Click on any column header to sort the results in ascending or descending order.")
        df_positions = pd.DataFrame(rows)

        # Add a Total P&L summary row at the bottom
        def parse_pnl(val):
            try:
                return float(str(val).replace('+$', '').replace('-$', '-').replace('$', '').replace(',', '').replace('—', '0'))
            except:
                return 0.0

        st.dataframe(
            df_positions,
            use_container_width=True,
            hide_index=True,
        )

        import io as _io
        excel_buf = _io.BytesIO()
        df_positions.to_excel(excel_buf, index=False, sheet_name='Positions')
        excel_buf.seek(0)
        st.download_button(
            label="⬇️ Export Positions to Excel",
            data=excel_buf,
            file_name="positions.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        # ── Collect chart data once — used by both charts
        chart_data = []
        for sym, t in sorted(trades.items()):
            for i, cycle in enumerate(build_cycles(sym, t), 1):
                if cycle['situation'] not in ('exercised', 'open'):
                    continue
                    # Exclude open positions with no options sold — no ROI calculable
                if cycle['situation'] == 'open' and not any((o['qty'] or 0) < 0 for o in cycle['opts']):
                    continue
                be, profit, roi, ann_roi, days, total_pnl = calc_cycle(cycle)
                if roi is None:
                    continue
                cycles_for_sym = build_cycles(sym, t)
                label = f"{sym} T{i}" if len(cycles_for_sym) > 1 else sym
                status = 'Open' if cycle['situation'] == 'open' else 'Closed'
                if roi < 0:
                    color = '#f87171'   # red — negative ROI
                elif status == 'Open':
                    color = '#fb923c'   # orange — open position
                else:
                    color = '#4ade80'   # green — closed profitable
                chart_data.append({
                    'label':     label,
                    'roi':       round(roi, 2),
                    'ann_roi':   round(ann_roi, 2) if (ann_roi is not None and status == 'Closed') else None,
                    'days':      days if days else 0,
                    'total_pnl': round(total_pnl, 2) if total_pnl else 0,
                    'status':    status,
                    'color':     color,
                })

        if chart_data:
            import plotly.graph_objects as go

            def make_bar_chart(data, y_key, title, y_label, extra_roi=False, sort_by_label=False):
                data_sorted = sorted(data, key=lambda c: c["label"] if sort_by_label else c[y_key])
                fig = go.Figure(go.Bar(
                    x=[c['label'] for c in data_sorted],
                    y=[c[y_key] for c in data_sorted],
                    marker_color=[c['color'] for c in data_sorted],
                    marker_opacity=0.9,
                    customdata=[
                        [c['label'], c[y_key], c['total_pnl'], c['days'], c['status'], c.get('roi', 0)]
                        for c in data_sorted
                    ],
                    hovertemplate=(
                        '<b>%{customdata[0]}</b><br>'
                        + (f'ROI: %{{customdata[5]:.2f}}%<br>' if extra_roi else '')
                        + f'{y_label}: %{{customdata[1]:.2f}}%<br>'
                        'Total P&L: $%{customdata[2]:,.2f}<br>'
                        'Days Held: %{customdata[3]}d<br>'
                        'Status: %{customdata[4]}<extra></extra>'
                    ),
                ))
                fig.add_hline(y=0, line_dash='dot', line_color='rgba(255,255,255,0.2)', line_width=1)
                fig.update_layout(
                    title=dict(text=title, font=dict(size=14)),
                    xaxis=dict(title='', showgrid=False, tickangle=-30),
                    yaxis=dict(title=y_label, showgrid=True,
                               gridcolor='rgba(255,255,255,0.07)', zeroline=False),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='rgba(255,255,255,0.75)', size=12),
                    margin=dict(l=40, r=20, t=50, b=70),
                    height=400,
                    hoverlabel=dict(bgcolor='#1e1e2e', font_size=13),
                    bargap=0.3,
                )
                return fig

            # Chart 1: ROI % per trade (all positions)
            st.markdown("#### ROI % Per Trade")
            st.caption(
                "Sorted alphabetically by ticker — Stocks bought during this period only | Green: Closed Trade, Orange: Open Trade")
            st.plotly_chart(make_bar_chart(chart_data, 'roi', '', 'ROI %', sort_by_label=True),
                            use_container_width=True)

            # Chart 2: Annualised ROI — closed positions only
            ann_data = [c for c in chart_data if c['ann_roi'] is not None]
            if ann_data:
                st.markdown("#### Annualised ROI % Per Trade")
                st.caption("Sorted from least to most profitable — Closed positions only")
                st.plotly_chart(make_bar_chart(ann_data, 'ann_roi', '', 'Annualised ROI %', extra_roi=True),
                                use_container_width=True)

            # Chart 3: Cumulative P&L line chart
            # Use sell_date for closed, buy_date for open; sort chronologically
            cum_points = []
            for sym, t in trades.items():
                for cycle in build_cycles(sym, t):
                    if cycle['situation'] not in ('exercised', 'open', 'sell_only', 'options_only'):
                        continue
                    be, profit, roi, ann_roi, days, total_pnl = calc_cycle(cycle)
                    if total_pnl is None:
                        continue
                    # Use close/latest date depending on situation
                    if cycle['situation'] == 'options_only':
                        opt_dates = [o.get('date', '') for o in cycle['opts'] if o.get('date')]
                        point_date = max(opt_dates) if opt_dates else None
                    else:
                        point_date = cycle.get('sell_date') or cycle.get('buy_date')
                    if not point_date:
                        continue
                    cycles_for_sym = build_cycles(sym, t)
                    i = next((i for i, c in enumerate(cycles_for_sym, 1) if c is cycle), 1)
                    label = f"{sym} T{i}" if len(cycles_for_sym) > 1 else sym
                    if cycle['situation'] == 'open':
                        status = 'Open'
                    elif cycle['situation'] == 'options_only':
                        status = 'Options Only'
                    elif cycle['situation'] == 'sell_only':
                        status = 'Closed (prior buy)'
                    else:
                        status = 'Closed'
                    cum_points.append({
                        'date':      point_date,
                        'label':     label,
                        'total_pnl': round(total_pnl, 2),
                        'roi':       round(roi, 2) if roi else 0,
                        'status':    status,
                    })

            if cum_points:
                cum_points.sort(key=lambda p: p['date'])
                # Build cumulative running total
                running = 0
                for p in cum_points:
                    running += p['total_pnl']
                    p['cumulative_pnl'] = round(running, 2)

                fig3 = go.Figure()

                # Shaded area under/over zero
                fig3.add_trace(go.Scatter(
                    x=[p['date'] for p in cum_points],
                    y=[p['cumulative_pnl'] for p in cum_points],
                    mode='lines+markers',
                    line=dict(color='#4ade80', width=2.5),
                    marker=dict(size=8, color='#4ade80',
                                line=dict(width=1.5, color='rgba(255,255,255,0.4)')),
                    fill='tozeroy',
                    fillcolor='rgba(74,222,128,0.12)',
                    customdata=[
                        [p['label'], p['total_pnl'], p['cumulative_pnl'], p['roi'], p['status']]
                        for p in cum_points
                    ],
                    hovertemplate=(
                        '<b>%{customdata[0]}</b><br>'
                        'Date: %{x}<br>'
                        'Trade P&L: $%{customdata[1]:,.2f}<br>'
                        'Cumulative P&L: $%{customdata[2]:,.2f}<br>'
                        'ROI: %{customdata[3]:.2f}%<br>'
                        'Status: %{customdata[4]}<extra></extra>'
                    ),
                    showlegend=False,
                ))

                fig3.add_hline(y=0, line_dash='dot',
                               line_color='rgba(255,255,255,0.2)', line_width=1)

                fig3.update_layout(
                    title=dict(text='', font=dict(size=14)),
                    xaxis=dict(title='', showgrid=False, tickangle=-30),
                    yaxis=dict(title='Cumulative P&L ($)', showgrid=True,
                               gridcolor='rgba(255,255,255,0.07)', zeroline=False),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='rgba(255,255,255,0.75)', size=12),
                    margin=dict(l=60, r=20, t=50, b=70),
                    height=400,
                    hoverlabel=dict(bgcolor='#1e1e2e', font_size=13),
                )
                st.markdown("#### Cumulative P&L")
                st.plotly_chart(fig3, use_container_width=True)

    st.divider()

# ── RENDER CYCLE ──────────────────────────────────────────────────────────────

def render_cycle(cycle, cycle_num, total_cycles, sym=''):
    situation = cycle['situation']
    rows = []

    for t in cycle['stock']:
        is_buy = (t['qty'] or 0) > 0
        rows.append({
            'Type':     'Stock',
            'Date':     t.get('date', ''),
            'Action':   'Buy' if is_buy else 'Sell',
            'Qty':      fq(t['qty']),
            'T. Price': fp(t['t_price']),
        })

    def opt_label(o):
        cp_label = 'Call Option' if o['cp'] == 'C' else 'Put Option'
        strike_str = str(int(o['strike'])) if o['strike'] == int(o['strike']) else str(o['strike'])
        return f"{cp_label} — {o['expiry']} {strike_str} {o['cp']}"

    for o in sorted(cycle['opts'], key=lambda o: o.get('date', '')):
        is_call = o['cp'] == 'C'
        qty = o['qty'] or 0
        if is_call:
            t_price = -(o['t_price'] or 0) if qty < 0 else +(o['t_price'] or 0)
            action  = 'Sell' if qty < 0 else 'Close'
        else:
            t_price = +(o['t_price'] or 0) if qty > 0 else -(o['t_price'] or 0)
            action  = 'Buy' if qty > 0 else 'Close'
        rows.append({'Type': opt_label(o), 'Date': o.get('date', ''),
                     'Action': action, 'Qty': fq(qty),
                     'T. Price': fp(t_price, sign=True)})

    if total_cycles > 1:
        if cycle_num > 1:
            st.divider()
        st.markdown(f"#### {sym} — Trade {cycle_num}")
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    be, profit, roi, ann_roi, days, total_pnl = calc_cycle(cycle)

    if situation in ('exercised', 'open'):
        has_options_sold = situation == 'open' and any((o['qty'] or 0) < 0 for o in cycle['opts'])
        if situation == 'open' and not has_options_sold:
            pass  # caption shown below in notes block
        else:
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Breakeven Price", fp(be, decimals=2))
            c2.metric("Profit / Share",  fp(profit, sign=True, decimals=4))
            c3.metric("ROI", fpct(roi), delta_color="normal" if (roi or 0) >= 0 else "inverse")
            c4.metric("Total P&L", fp(total_pnl, sign=True, decimals=2) if total_pnl is not None else '—',
                      delta_color="normal" if (total_pnl or 0) >= 0 else "inverse")
            c5.metric("Days Held" if situation == 'exercised' else "Days Open", fdays(days) if situation == 'exercised' else '—')
    elif situation == 'sell_only':
        if total_pnl is not None:
            st.metric("Total P&L (Options sold)", fp(total_pnl, sign=True, decimals=2),
                      delta_color="normal" if (total_pnl or 0) >= 0 else "inverse")
    elif situation == 'options_only':
        if total_pnl is not None:
            st.metric("Total P&L (Options sold)", fp(total_pnl, sign=True, decimals=2),
                      delta_color="normal" if (total_pnl or 0) >= 0 else "inverse")

    has_options_sold = situation == 'open' and any((o['qty'] or 0) < 0 for o in cycle['opts'])
    notes = {
        'exercised':    "📌 Full cycle — Stock bought and sold in this period.",
        'sell_only':    "📌 Stock sold — Original buy was in a prior period, profit is the option premium collected during this period | Insufficient data to run full calculations.",
        'options_only': "📌 Options only — Original buy was in a prior period, profit is the option premium collected during this period | Insufficient data to run full calculations.",
    }
    if situation == 'open' and has_options_sold:
        st.caption("📌 Stock still open — Profit is the option premium collected during this period | Insufficient data to run full calculations.")
    elif situation == 'open' and not has_options_sold:
        st.caption("📌 Stock still open — No options sold during this period.")
    else:
        st.caption(notes.get(situation, ''))


def render_ticker(sym, trades):
    cycles = build_cycles(sym, trades)
    with st.expander(sym, expanded=False):
        for i, cycle in enumerate(cycles, 1):
            render_cycle(cycle, i, len(cycles), sym=sym)

# ── HOW CALCULATIONS WORK (always visible at bottom when file loaded) ─────────

def render_how_it_works():
    with st.expander("How Calculations Work"):
        st.caption("Source: Only the Trades section (Stocks + Equity and Index Options).")
        st.dataframe(pd.DataFrame([
            ["Breakeven",              "Stock Buy Price − Net Options Premium"],
            ["Profit/Share (exercised)", "Strike Price – Breakeven"],
            ["Profit/Share (open)",    "Net Options Premium"],
            ["ROI",                    "(Profit ÷ Stock Buy Price) × 100"],
        ], columns=["Metric", "Formula"]), hide_index=True, use_container_width=True)

# ── UI ────────────────────────────────────────────────────────────────────────

st.markdown("### Upload The Trading Statement (PDF)")
uploaded = st.file_uploader(
    "", type=["pdf"], key="uploader"
)

if uploaded:
    st.caption(f"📄 Loaded: **{uploaded.name}** ({uploaded.size:,} bytes)")

    with st.spinner("Parsing..."):
        try:
            text = extract_text(uploaded)
        except Exception as e:
            st.error(f"Could not read PDF: {e}")
            st.stop()

        if len(text.strip()) < 100:
            st.error("No text extracted — PDF may be image-based (scanned).")
            st.stop()

        period = parse_period(text)
        section, fmt, debug = find_trades_section(text)
        trades = parse_trades(section, fmt)

    if not trades:
        st.error("No trades found.")
        st.json(debug)
        with st.expander("Raw extracted text"):
            st.text(text[:4000])
        with st.expander("Trades section extracted"):
            st.text(section[:2000])
        st.stop()

    # Portfolio dashboard
    render_dashboard(trades, period=period)

    # Per-ticker detail
    st.markdown("#### Trades Breakdown")
    tickers = sorted(trades.keys())

    for sym in tickers:
        render_ticker(sym, trades[sym])

    # Always visible at bottom
    st.divider()
    render_how_it_works()

else:
    render_how_it_works()

