import streamlit as st
from itertools import combinations
from math import gcd, log, ceil
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
        st.metric("分数", f"{favorable}/{total}")
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

        st.caption(
            "⚠️ 各行の分数を合計しても、全体の分数とは一致しません。"
            "1回の出目が複数の行に同時にカウントされることがあるためです。\n\n"
            "例：出目 [1, 6, 2, 5]（6,7,8 を選択中）のとき、"
            "ペアの組み方は (7,7) / (3,11) / (6,8) の3通りになります。"
            "このとき「7+7」と「6+8」の両方にカウントされます。"
        )

