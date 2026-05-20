import numpy as np
def below_threshold_len(percent, texts):
    # cnt = 0
    # for text in texts:
    #     if len(text.split()) <= threshold:
    #         cnt += 1
    # return f'{cnt/len(texts)*100:.2f}%'
    text_lengths = [len(text.split()) for text in texts]
    max_len = int(np.percentile(text_lengths, percent)) # percentile로 전체데이터의 95%지점 찾기
    return max_len

def below_threshold_len_split(percent, texts):
    # cnt = 0
    # for text in texts:
    #     if len(text.split()) <= threshold:
    #         cnt += 1
    # return f'{cnt/len(texts)*100:.2f}%'
    text_lengths = [len(text) for text in texts]
    max_len = int(np.percentile(text_lengths, percent)) # percentile로 전체데이터의 95%지점 찾기
    return max_len

def rare_word_status(threshold, word_count_list):
    # 등장 빈도수가 threshold회 미만인 단어들이 이 데이터에서 얼만큼의 비중을 차지하는지 확인
    total_cnt = rare_cnt = total_freq = rare_freq = 0

    for _, freq in word_count_list:
        total_cnt += 1
        total_freq += freq
        if freq < threshold:
            rare_cnt += 1
            rare_freq += freq

    print(f'전체단어 : {total_cnt:,}개 {total_freq:,}번')
    print(f'희귀단어 : {rare_cnt:,}개 {rare_freq:,}번')
    print(f'희귀단어비율 : {rare_cnt/total_cnt * 100:.2f}%, 빈도수 비율 : {rare_freq/total_freq*100:.2f}%')
    use_cnt = total_cnt - rare_cnt
    use_freq = total_freq - rare_freq
    print(f'희귀 단어를 뺀 단어 수 : {use_cnt:,}개 {use_freq/total_freq * 100:.2f}%')
    # 22647개만 해도 전체 빈도 중 98% 차지하기때문에 효율적인 num_words지정 가능