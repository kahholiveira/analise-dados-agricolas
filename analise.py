
import subprocess, csv

def rodar_query(query):
    result = subprocess.run(
        ["sudo", "-u", "postgres", "psql", "-d", "analise_agricola",
         "-t", "-A", "-F", ",", "-c", query],
        capture_output=True, text=True
    )
    return [l.split(",") for l in result.stdout.strip().split("\n") if l]

dados = rodar_query("""
SELECT p.produto, p.regiao, p.quantidade_kg, pm.preco_kg,
       ROUND((p.quantidade_kg * pm.preco_kg)::numeric,2),
       c.custo_producao,
       ROUND((p.quantidade_kg * pm.preco_kg - c.custo_producao)::numeric,2)
FROM producao p
JOIN preco_mercado pm ON p.produto = pm.produto
JOIN custos c ON p.produto = c.produto
ORDER BY 7 DESC;
""")

produtos  = [d[0] for d in dados]
regioes   = [d[1] for d in dados]
receitas  = [float(d[4]) for d in dados]
custos_v  = [float(d[5]) for d in dados]
lucros    = [float(d[6]) for d in dados]

print("=" * 55)
print("   LUCRO POR PRODUTO")
print("=" * 55)
max_l = max(lucros)
for i, p in enumerate(produtos):
    barra = int((lucros[i] / max_l) * 30)
    cor = "\033[92m" if lucros[i] > 0 else "\033[91m"
    print(f"{p:<12} {cor}{'|' * barra}\033[0m R$ {lucros[i]:>10,.2f}")

print()
print("=" * 55)
print("   PREVISAO DE LUCRO FUTURO (+10% ao ano)")
print("=" * 55)
print(f"{'Produto':<12} {'2024':>12} {'2025':>12} {'2026':>12}")
print("-" * 55)
for i, p in enumerate(produtos):
    print(f"{p:<12} R${lucros[i]:>9,.0f} R${lucros[i]*1.1:>9,.0f} R${lucros[i]*1.21:>9,.0f}")

with open("/tmp/dados_agricola.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["produto","regiao","receita","custo","lucro","lucro_2025","lucro_2026"])
    for i in range(len(produtos)):
        w.writerow([produtos[i], regioes[i], receitas[i], custos_v[i],
                    lucros[i], round(lucros[i]*1.1,2), round(lucros[i]*1.21,2)])

print()
print("CSV salvo em: /tmp/dados_agricola.csv")
print(f"Total lucro: R$ {sum(lucros):,.2f}")
print(f"Mais lucrativo: {produtos[0]}")
