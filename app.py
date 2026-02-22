import streamlit as st
from itertools import combinations
from math import gcd, log, ceil

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

    st.success("計算完了！")
    st.markdown("---")

    trials_until_below_50 = ceil(log(0.5) / log(prob))

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("確率（%）", f"{prob * 100:.2f}%")
    with col_b:
        st.metric("分数", f"{favorable}/{total}")
    with col_c:
        st.metric("連続成功が50%を切る試行回数", f"{trials_until_below_50}回")
