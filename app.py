import streamlit as st
from itertools import combinations
from math import gcd, log, ceil
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import pandas as pd


def calculate_detailed_probabilities(targets):
    targets = sorted(targets)
    target_set = set(targets)

    pairs = {}
    for i, t1 in enumerate(targets):
        for t2 in targets[i:]:
            pairs[(t1, t2)] = 0

    singles = {t: 0 for t in targets}
    total = 0

    for a in range(1, 7):
        for b in range(1, 7):
            for c in range(1, 7):
                for d in range(1, 7):
                    total += 1
                    pairings = [(a+b, c+d), (a+c, b+d), (a+d, b+c)]

                    for (t1, t2) in pairs:
                        for s1, s2 in pairings:
                            if (s1 == t1 and s2 == t2) or (s1 == t2 and s2 == t1):
                                pairs[(t1, t2)] += 1
                                break

                    has_target_pair = any(
                        s1 in target_set and s2 in target_set
                        for s1, s2 in pairings
                    )
                    if not has_target_pair:
                        achievable = set()
                        for s1, s2 in pairings:
                            if s1 in target_set:
                                achievable.add(s1)
                            if s2 in target_set:
                                achievable.add(s2)
                        for t in achievable:
                            singles[t] += 1

    pair_result = {k: (v / total, v, total) for k, v in pairs.items()}
    single_result = {t: (v / total, v, total) for t, v in singles.items()}
    return pair_result, single_result


def calculate_dice_probability(targets):
    total_outcomes = 0
    favorable_outcomes = 0

    for a in range(1, 7):
        for b in range(1, 7):
            for c in range(1, 7):
                for d in range(1, 7):
                    total_outcomes += 1
                    dices = [a, b, c, d]
                    is_favorable = False
                    for pair in combinations(range(4), 2):
                        s = dices[pair[0]] + dices[pair[1]]
                        if s in targets:
                            is_favorable = True
                            break
                    if is_favorable:
                        favorable_outcomes += 1

    probability = favorable_outcomes / total_outcomes
    g = gcd(favorable_outcomes, total_outcomes)
    return probability, favorable_outcomes, total_outcomes, favorable_outcomes // g, total_outcomes // g


def draw_venn(targets, pair_probs, single_probs):
    colors = ['#5B8DBE', '#E07B39', '#3DAA6A']
    alpha = 0.32

    def label(data):
        p, fav, tot = data
        return f"{p*100:.1f}%\n({fav}/{tot})"

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_aspect('equal')
    ax.axis('off')

    if len(targets) == 2:
        t1, t2 = targets
        ax.set_xlim(-1.8, 1.8)
        ax.set_ylim(-1.2, 1.2)

        ax.add_patch(Circle((-0.45, 0), 0.75, alpha=alpha, fc=colors[0], ec=colors[0], lw=2))
        ax.add_patch(Circle(( 0.45, 0), 0.75, alpha=alpha, fc=colors[1], ec=colors[1], lw=2))

        ax.text(-0.45, 1.0, str(t1), ha='center', va='center', fontsize=20, fontweight='bold', color=colors[0])
        ax.text( 0.45, 1.0, str(t2), ha='center', va='center', fontsize=20, fontweight='bold', color=colors[1])

        ax.text(-0.9,  0.18, f"{t1}\n{label(single_probs[t1])}", ha='center', va='center', fontsize=12)
        ax.text(-0.9, -0.25, f"{t1}+{t1}\n{label(pair_probs[(t1, t1)])}", ha='center', va='center', fontsize=10, color='#444444')
        ax.text( 0.9,  0.18, f"{t2}\n{label(single_probs[t2])}", ha='center', va='center', fontsize=12)
        ax.text( 0.9, -0.25, f"{t2}+{t2}\n{label(pair_probs[(t2, t2)])}", ha='center', va='center', fontsize=10, color='#444444')
        ax.text(   0,     0, f"{t1} & {t2}\n{label(pair_probs[(t1, t2)])}", ha='center', va='center', fontsize=12)

    elif len(targets) == 3:
        t1, t2, t3 = targets
        ax.set_xlim(-2.0, 2.0)
        ax.set_ylim(-2.05, 1.8)

        ax.add_patch(Circle((-0.5,  0.35), 0.75, alpha=alpha, fc=colors[0], ec=colors[0], lw=2))
        ax.add_patch(Circle(( 0.5,  0.35), 0.75, alpha=alpha, fc=colors[1], ec=colors[1], lw=2))
        ax.add_patch(Circle(( 0.0, -0.45), 0.75, alpha=alpha, fc=colors[2], ec=colors[2], lw=2))

        ax.text(-0.8,  1.25, str(t1), ha='center', va='center', fontsize=20, fontweight='bold', color=colors[0])
        ax.text( 0.8,  1.25, str(t2), ha='center', va='center', fontsize=20, fontweight='bold', color=colors[1])
        ax.text( 0.0, -1.62, str(t3), ha='center', va='center', fontsize=20, fontweight='bold', color=colors[2])

        # Single-only + same-number doubles per exclusive region
        ax.text(-1.1,  0.58, f"{t1}\n{label(single_probs[t1])}", ha='center', va='center', fontsize=11)
        ax.text(-1.1,  0.20, f"{t1}+{t1}\n{label(pair_probs[(t1, t1)])}", ha='center', va='center', fontsize=10, color='#444444')
        ax.text( 1.1,  0.58, f"{t2}\n{label(single_probs[t2])}", ha='center', va='center', fontsize=11)
        ax.text( 1.1,  0.20, f"{t2}+{t2}\n{label(pair_probs[(t2, t2)])}", ha='center', va='center', fontsize=10, color='#444444')
        ax.text( 0.0, -0.70, f"{t3}\n{label(single_probs[t3])}", ha='center', va='center', fontsize=11)
        ax.text( 0.0, -1.20, f"{t3}+{t3}\n{label(pair_probs[(t3, t3)])}", ha='center', va='center', fontsize=10, color='#444444')

        # Pair intersection regions
        ax.text( 0.0,  0.70, f"{t1}&{t2}\n{label(pair_probs[(t1, t2)])}", ha='center', va='center', fontsize=11)
        ax.text(-0.52, -0.18, f"{t1}&{t3}\n{label(pair_probs[(t1, t3)])}", ha='center', va='center', fontsize=11)
        ax.text( 0.52, -0.18, f"{t2}&{t3}\n{label(pair_probs[(t2, t3)])}", ha='center', va='center', fontsize=11)

        # Center (all 3 simultaneously is impossible with one pairing)
        ax.text(0, 0.12, "0%", ha='center', va='center', fontsize=10, color='gray')

    plt.tight_layout()
    return fig


st.title("🎲 Can't Stop - サイコロ確率計算")
st.markdown("4つのサイコロを振ったとき、いずれかの2つの組み合わせが指定した数になる確率を計算します。")

if "selected" not in st.session_state:
    st.session_state.selected = set()

st.subheader("目標の数を選択（最大3つ）")

cols = st.columns(11)
for i, n in enumerate(range(2, 13)):
    with cols[i]:
        is_selected = n in st.session_state.selected
        if st.button(str(n), key=f"btn_{n}", type="primary" if is_selected else "secondary", use_container_width=True):
            if is_selected:
                st.session_state.selected.discard(n)
            elif len(st.session_state.selected) < 3:
                st.session_state.selected.add(n)
            st.rerun()

targets = sorted(st.session_state.selected)

if targets:
    st.markdown(f"**選択中:** {targets}")
else:
    st.info("数字ボタンを押して目標を選択してください（最大3つ）")

if st.button("確率を計算", type="primary", disabled=len(targets) == 0):
    with st.spinner("計算中..."):
        prob, favorable, total, simp_num, simp_den = calculate_dice_probability(set(targets))
        pair_probs, single_probs = calculate_detailed_probabilities(set(targets))

    st.success("計算完了！")
    st.markdown("---")

    trials_until_below_50 = ceil(log(0.5) / log(prob))

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("確率（%）", f"{prob * 100:.2f}%")
    with col_b:
        st.metric("場合の数", f"{favorable}/{total}")
    with col_c:
        st.metric("連続成功が50%を切る試行回数", f"{trials_until_below_50}回")

    if len(targets) >= 2:
        st.markdown("---")
        st.subheader("詳細確率")

        rows = []
        for t in targets:
            p, fav, tot = single_probs[t]
            rows.append({"状況": f"{t} のみ", "確率": f"{p*100:.2f}%", "分数": f"{fav}/{tot}"})
        for t in targets:
            p, fav, tot = pair_probs[(t, t)]
            rows.append({"状況": f"{t} + {t}", "確率": f"{p*100:.2f}%", "分数": f"{fav}/{tot}"})
        for i, t1 in enumerate(targets):
            for t2 in targets[i+1:]:
                p, fav, tot = pair_probs[(t1, t2)]
                rows.append({"状況": f"{t1} + {t2}", "確率": f"{p*100:.2f}%", "分数": f"{fav}/{tot}"})

        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        st.markdown("---")
        with st.expander("ベン図を表示"):
            st.caption("各領域：その数字のみ or 2つ同時に出せる確率。中心の0%は4つのサイコロ1組の振りで3つ同時は不可能なため。")
            fig = draw_venn(targets, pair_probs, single_probs)
            st.pyplot(fig)
            plt.close(fig)

