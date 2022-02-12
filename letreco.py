import numpy as np
np.set_printoptions(precision=2, suppress=True, linewidth=300, edgeitems=20)  # For compact display.

import dash
# from dash import dash_table
from dash import html
from dash import dcc
from dash.dependencies import Input, Output, State, ClientsideFunction

from itertools import product

import unidecode
import string

import numpy as np
import pickle

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(
    __name__, 
    external_stylesheets=external_stylesheets,
    external_scripts=["https://cdnjs.cloudflare.com/ajax/libs/dragula/3.7.2/dragula.min.js"],
)
server = app.server 

app_margins = "15%"
btn_green_style={"color":"white", 'display': 'inline-block', "float":"left"}

intro=""" Recomendador de palpites para Letreco e jogos tipo WORDLE em português.
No seu aplicativo de escolha selecione uma palavra inicial. Algumas boas são 'raios' e 'serao'.
Escreva a sua escolha na primeira caixa de texto e aperte os botões para informar a cores do feedback.
Depois aperte o botão RECOMENDAR que aqui mesmo aparecerá um conjunto de palavras possíveis de serem a correta e ainda uma recomendação para o seu próximo palpite.
"""

app.layout = html.Div([
    html.Div(id="app_div", style={'margin-left': app_margins, 'margin-right': app_margins}, children=[
        html.Div(id=f"palpite_div_{palpite}", style={'margin-left': app_margins, 'margin-right': app_margins, "float":"left"}, 
            children=([dcc.Input(id=f"input_{palpite}", type="text", placeholder="", style={'marginRight':'10px'}),
                        html.Div(style={"float":"right"}, children = [
                                    html.Button(id=f'p{palpite}c{char}',style=btn_green_style, n_clicks=0) for char in range(5)
                                ])
                    ])
            
        ) for palpite in range(6)
    ]),
    html.H1("."), 
    html.H1("."), 
    html.H1("."),
    html.H1("."),
    html.Div(id="output_div", style={'margin-left': app_margins, 'margin-right': app_margins}, children=[
        html.H1("PALPITECO"),
        html.H3("Sempre comece o Letreco com 'raios' ou 'serao'."),
        html.Button("RECOMENDAR", id=f'recomendar',style={"color":"white","background-color":"green", 'display': 'inline-block'}, n_clicks=0) ,
        html.P(intro, id=f'output', style={"font-size":"normal", "color":"DarkGreen"}),
        html.P(id=f'palpite_quality', style={"font-size":"normal", "color":"DarkGreen"}),
        html.P(id=f'lexico', style={"font-size":"normal", "color":"DarkGreen"}),
        html.P(id=f'recomendacao', style={"font-size":"normal", "color":"DarkGreen"}),
        html.H1("."), 
        html.H1("."), 
        html.H5("Jogos tipo WORDLE em português:"),
        html.A("Termooo, ", href="https://term.ooo/", target="_blank"),
        html.A("Charada, ", href="https://charada.vercel.app/", target="_blank"),
        html.A("Letreco, ", href="https://www.gabtoschi.com/letreco/", target="_blank"),
        html.A("Palavra do dia, ", href="https://palavra-do-dia.pt/", target="_blank"),
        html.A("Olavooo, ", href="https://olav.ooo/", target="_blank"),
        html.A("WORDLE, ", href="https://wordlegame.org/wordle-in-portuguese", target="_blank"),
    ]),
])

@app.callback([Output(f'p{palpite}c{char}', 'children') for palpite in range(6) for char in range(5)],
            [Input(f'input_{palpite}', 'value') for palpite in range(6)])
def atualizar_cor_botao(*argv):
    letters = []
    for palpite in argv:
        if palpite is None:
            palpite = ""
        palpite = unidecode.unidecode(palpite)
        palpite = palpite.translate(str.maketrans('', '', string.punctuation)).lower()
        palpite_pad = palpite.ljust(5, ' ')
        for char in range(5):
            letters.append(palpite_pad[char])
    return letters

@app.callback([Output(f'p{palpite}c{char}', 'style') for char in range(5) for palpite in range(6)],
            [Input(f'p{palpite}c{char}', 'n_clicks') for char in range(5) for palpite in range(6)])
def atualizar_cor_botao(*argv):
    states = ["LightGray", "LightCoral", "#fdf29b", "LightGreen"]
    return [{"background-color":states[arg % 4]} for arg in argv]


def uncertainty(verde, amarelo, laranja, vermelho, isin_pos, isin, l3):
    if len(verde) + len(amarelo) > 0:
        uncert_set = set.intersection(*([isin_pos[cp] for cp in verde] + [isin[c] for c in amarelo]))
    else:
        uncert_set = set(l3)
    if len(vermelho) > 0:
        uncert_set -= set.union(*([isin_pos[cp] for cp in laranja] + [isin[c] for c in vermelho]))
        
    return uncert_set


def recomendar(palpites):    
    with open('word_count_filter.pkl', 'rb') as p:
        word_count = pickle.load(p)

    lexico_wiki = [w for w,c in word_count.items() if (c > 100) and (w[0].isupper() == False) and (any(char.isdigit() for char in w)==False)] #sorted(, key=lambda x:-x[1])
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    isin = {c:set([w for w in lexico_wiki if c in w]) for c in alphabet}
    isin_pos = {cp:set([w for w in lexico_wiki if cp in set(enumerate(w))]) for cp in list(product(range(5),alphabet))}

    palpite_letras = "".join([w for w, pat in palpites])

    verde_entrada = set()
    amarelo_entrada = set()
    laranja_entrada = set()
    vermelho_entrada = set()

    for p in palpites:
        word =p[0]
        pattern = p[1]
        for i in range(5):
            if   pattern[i] == "g":
                verde_entrada.add((i,word[i]))
                amarelo_entrada.add(word[i])
            elif pattern[i] == "y":
                amarelo_entrada.add(word[i])
                laranja_entrada.add((i, word[i]))
            elif pattern[i] == "r":
                vermelho_entrada.add(word[i])

    vermelho_entrada -= amarelo_entrada
    laranja_entrada -= verde_entrada


    lexico = uncertainty(verde_entrada, amarelo_entrada, laranja_entrada, vermelho_entrada, isin_pos, isin, lexico_wiki)

    # print(len(lexico))
    # if len(lexico) <= 10:
    #     print(lexico)

    isin_lexico = {c:set([w for w in lexico if c in w]) for c in alphabet}

    isin_pos_lexico = {cp:set([w for w in lexico if cp in set(enumerate(w))]) for cp in list(product(range(5),alphabet))}

    performance_restrito = {}

    lexico_wiki = [w for w in lexico_wiki if len(set(w) - set(alphabet))==0]

    for w_palpite in lexico_wiki: #set(l3):# - set.union(*[isin[c] for c in set(palpite_letras)]):
        if w_palpite not in performance_restrito.keys():
            lens = []
            for w_do_dia in set(lexico)-set([w_palpite]):
                verde = set(enumerate(w_palpite)) & set(enumerate(w_do_dia))
                amarelo = set(w_palpite) & set(w_do_dia)
                laranja = set([(i,w) for (i,w) in set(enumerate(w_palpite)) if w in amarelo]) - verde
                vermelho = set(w_palpite) - set(w_do_dia) - amarelo
                uncert_set = uncertainty(verde, amarelo, laranja, vermelho, isin_pos_lexico, isin_lexico, lexico)

                lens.append(len(uncert_set))
            performance_restrito[w_palpite] = lens
        #print(".", end="")


    ranking_palpites_exaustivo = sorted([(w,np.percentile(performance_restrito[w], 100)) for w in performance_restrito.keys() if len(performance_restrito[w]) > 0], key=lambda x:x[1])

    return len(lexico), list(lexico)[:30], [(x,c) for x,c in ranking_palpites_exaustivo][:5]


@app.callback([Output('output', 'children'),
                Output('palpite_quality','children'),
                Output('lexico','children'),
                Output('recomendacao','children')],
                Input("recomendar", "n_clicks"),
                State('output', 'children'),
                State("app_div", "children"))
def recomendarx(nClicks, texto_atual, app_div):
    if nClicks == 0:
        return [texto_atual], [], [], []

    translate_cores = {"LightGray":"x", "LightCoral":"r", "#fdf29b":"y", "LightGreen":"g"}

    palpites_input = []
    # print("app_div", app_div[0]["props"]["children"][1]["props"]["children"][0]["props"]["children"])
    for palpite in range(0,6):
        palpite_str = []
        cores_str = []
        for char in range(5):
            #print(app_div[palpite]["props"]["children"][char]["props"]["children"])
            if "children" in app_div[palpite]["props"]["children"][1]["props"]["children"][char]["props"].keys():
                caract = app_div[palpite]["props"]["children"][1]["props"]["children"][char]["props"]["children"]
            else:
                caract = "@"
            #print("caract", caract)
            if caract.isalpha():
                palpite_str.append(caract.lower())
            else:
                palpite_str.append("@")

            if "style"    in app_div[palpite]["props"]["children"][1]["props"]["children"][char]["props"].keys():
                if "background-color" in app_div[palpite]["props"]["children"][1]["props"]["children"][char]["props"]["style"].keys():
                    cor = app_div[palpite]["props"]["children"][1]["props"]["children"][char]["props"]["style"]["background-color"]
                    cor = translate_cores[cor]
                else:
                    cor = "x"
            else:
                cor = "x"
            cores_str.append(cor)
        palpites_input.append(tuple(["".join(palpite_str), "".join(cores_str)]))

    palpites_filter = [(p, c) for p,c in palpites_input if (" " not in p) and ("@" not in p) and ("x" not in c)]
    palpites_word_warning = [(p, c) for p,c in palpites_input if ((" " in p) or ("@" in p)) and (len(p.replace(" ", "").replace("@", "")) >0 )]
    palpites_color_warning = [(p, c) for p,c in palpites_input if ("x" in c) and (len(c.replace("x","")) > 0)]

    if len(palpites_filter) > 0:
        palpite_resposta = f"Os palpites {[w for w, c in palpites_filter]} estao sendo considerados. "
    else:
        palpite_resposta = f"Eu preciso de pelo menos um palpite válido para recomendar. "

    if len(palpites_word_warning) > 0:
        palpite_resposta += f"Os palpites {[w for w, c in palpites_word_warning]} estão com letras faltando. "
    if len(palpites_color_warning) > 0:
        palpite_resposta += f"Os palpites {[w for w, c in palpites_color_warning]} estão com cores faltando. "

    if len(palpites_filter) > 0: 
        lexico_len, lexico_sample, recomendacoes = recomendar(palpites_filter)

        lexico_resposta = f"Estou indeciso entre {lexico_len} palavras. Algumas delas são: {lexico_sample}. "
        if lexico_len <= 3:
            lexico_resposta += "Talvez já dê para chutar lá."
        if lexico_len >= 1:
            recomendacoes_resposta = f"Seu proximo palpite deveria ser uma dessas aqui:{[r for r, c in recomendacoes]}. Vale lembrar que é melhor usar o seu palpite para reduzir o conjunto das palavras possíveis. Portanto, ele pode não seguir as dicas anteriores."
        else:
            recomendacoes_resposta = ""
    else:
        lexico_resposta = ""
        recomendacoes_resposta = ""
    return [], [palpite_resposta], [lexico_resposta], [recomendacoes_resposta]

if __name__ == '__main__':
    app.run_server(debug=True)