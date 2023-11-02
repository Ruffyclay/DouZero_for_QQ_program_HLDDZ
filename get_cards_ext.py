import random


def sort_string(input_str):
    order = 'DX2AKQJT9876543'
    sorted_str = ''

    for char in order:
        count = input_str.count(char)
        if count > 0:
            sorted_str += char * count

    return sorted_str


def Creat_Card():
    card_type = ['', '', '', '']
    card_values = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']
    n = 1
    cards = ['D', 'X']
    for i in card_type:
        for j in card_values:
            cards.append((i + j))
            n += 1
    # print('牌库生成中.............')
    # print(cards.__len__())
    return cards


def WashAndPush_Card(cards):
    # print('洗牌中.............')
    random.shuffle(cards)
    # print('发牌中')

    # print('底 牌 : %s' % cards[0:3])

    player1 = sort_string(cards[3:20])
    player2 = sort_string(cards[20:37])
    player3 = sort_string(cards[37:54])
    dp = sort_string(cards[0:3])
    separator = ''

    player1 = separator.join(player1)
    player2 = separator.join(player2)
    player3 = separator.join(player3)
    dp = separator.join(dp)
    # print(player1, player2, player3, dp)
    # print('player1 : ' + str(player1))
    # print('player2 : ' + str(player2))
    # print('player3 : ' + str(player3))
    return player1, player2, player3, dp


if __name__ == '__main__':
    WashAndPush_Card(Creat_Card())
