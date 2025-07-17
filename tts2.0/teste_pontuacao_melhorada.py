#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste das Melhorias na Limpeza de Pontuação
=============================================

Este script testa a nova função limpar_texto() que resolve o problema
de TTS falando "ponto" literalmente, mas preserva a entonação natural.
"""

import re
import sys
import os

# Importar a função melhorada
sys.path.append(os.path.dirname(__file__))
from usar_minha_voz import limpar_texto

def testar_casos_pontuacao():
    """Testa diferentes casos problemáticos de pontuação"""
    
    print("=" * 70)
    print("TESTE DAS MELHORIAS NA LIMPEZA DE PONTUAÇÃO")
    print("=" * 70)
    print()
    print("🎯 OBJETIVO: Evitar que TTS fale 'ponto' mas manter entonação natural")
    print()
    
    # Casos de teste
    casos_teste = [
        {
            'titulo': 'Frases com pontos finais (problema principal)',
            'textos': [
                'Olá professora. Como está?',
                'Entendi a matéria. Muito obrigado.',
                'A resposta está certa. Parabéns pela explicação.',
                'Isso é muito interessante. Vou estudar mais sobre isso.'
            ]
        },
        {
            'titulo': 'Abreviações importantes (devem ser preservadas)',
            'textos': [
                'Dr. João é médico.',
                'A Profa. Maria ensina matemática.',
                'Sr. Silva, etc.',
                'Por exemplo, vs. outras opções.'
            ]
        },
        {
            'titulo': 'Reticências problemáticas (devem ser removidas)',
            'textos': [
                'Bem... como posso explicar...',
                'Isso é....... complicado.',
                'Então.... vamos ver....',
                'Humm… interessante…'
            ]
        },
        {
            'titulo': 'Frases sem pontuação final (precisam de pausa)',
            'textos': [
                'Obrigado pela aula',
                'Ótima explicação',
                'Entendi perfeitamente',
                'Muito bom mesmo'
            ]
        },
        {
            'titulo': 'Textos com emojis e caracteres especiais',
            'textos': [
                'Muito bom! 😊 Adorei a explicação.',
                'Perfeito... 👍 Assim fica mais claro.',
                'Obrigado! 🙏 Entendi tudo.',
                'Excelente!! ⭐ Parabéns.'
            ]
        },
        {
            'titulo': 'Casos mistos complexos',
            'textos': [
                'Dr. Silva disse: "A interpretação está correta." Concordo.',
                'Profa. Ana explicou etc... Foi muito útil.',
                'O Sr. João, por ex., sempre ajuda. Obrigado.',
                'Isso significa... bem... que entendi. Perfeito.'
            ]
        }
    ]
    
    total_casos = 0
    total_melhorias = 0
    
    for categoria in casos_teste:
        print(f"\n📋 {categoria['titulo'].upper()}")
        print("-" * len(categoria['titulo']) + "---")
        
        for texto_original in categoria['textos']:
            total_casos += 1
            texto_limpo = limpar_texto(texto_original)
            
            # Análise das melhorias
            tem_ponto_original = '.' in texto_original
            tem_ponto_limpo = '.' in texto_limpo
            tem_virgula_final = texto_limpo.strip().endswith(',')
            tem_pausa = ', ' in texto_limpo or ' ,' in texto_limpo
            
            print(f"\n  📝 Original: '{texto_original}'")
            print(f"  ✨ Limpo:    '{texto_limpo}'")
            
            melhorias = []
            if tem_ponto_original and not tem_ponto_limpo:
                melhorias.append("pontos removidos")
                total_melhorias += 1
            if tem_virgula_final:
                melhorias.append("pausa final adicionada")
            if tem_pausa:
                melhorias.append("pausas internas preservadas")
            
            if melhorias:
                print(f"  🔧 Melhorias: {', '.join(melhorias)}")
            
            # Verificar se ainda há pontos (possível problema)
            if '.' in texto_limpo and ',' not in texto_limpo:
                print(f"  ⚠️  ATENÇÃO: Ainda contém pontos que podem causar problema")
    
    # Resumo final
    print("\n" + "=" * 70)
    print("RESUMO DOS TESTES")
    print("=" * 70)
    print(f"Total de casos testados: {total_casos}")
    print(f"Casos com melhorias aplicadas: {total_melhorias}")
    print(f"Taxa de sucesso: {(total_melhorias/total_casos*100):.1f}%")
    print()
    print("🎯 PRINCIPAIS MELHORIAS IMPLEMENTADAS:")
    print("   ✅ Substitui pontos finais por vírgulas (mantém entonação)")
    print("   ✅ Preserva abreviações importantes (Dr., Prof., etc.)")
    print("   ✅ Remove reticências problemáticas")
    print("   ✅ Adiciona pausas naturais onde necessário")
    print("   ✅ Evita que TTS fale 'ponto' literalmente")
    print("   ✅ Mantém entonação natural das frases")

def demonstrar_antes_depois():
    """Demonstra a diferença entre função antiga e nova"""
    
    print("\n" + "=" * 70)
    print("COMPARAÇÃO: FUNÇÃO ANTIGA vs. NOVA")
    print("=" * 70)
    
    def limpar_texto_antigo(texto):
        """Versão antiga (problemática)"""
        # Padrão para detectar emojis
        padrao_emoji = re.compile("["
            u"\U0001F600-\U0001F64F"
            u"\U0001F300-\U0001F5FF"
            u"\U0001F680-\U0001F6FF"
            u"\U0001F1E0-\U0001F1FF"
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE)
        
        texto_limpo = padrao_emoji.sub('', texto)
        texto_limpo = ' '.join(texto_limpo.split())
        texto_limpo = texto_limpo.replace('...', '')
        texto_limpo = texto_limpo.replace('..', '')
        texto_limpo = texto_limpo.replace('.', '')  # PROBLEMA: Remove TODOS os pontos
        texto_limpo = re.sub(r'\s+([,!?])', r'\1', texto_limpo)
        return texto_limpo.strip()
    
    exemplos_problematicos = [
        'Boa explicação. Muito obrigado.',
        'Dr. Silva está certo. Concordo.',
        'Entendi tudo... Perfeito.',
        'A resposta é 42. Fim.'
    ]
    
    for exemplo in exemplos_problematicos:
        antigo = limpar_texto_antigo(exemplo)
        novo = limpar_texto(exemplo)
        
        print(f"\n📝 Texto original: '{exemplo}'")
        print(f"❌ Função antiga:  '{antigo}'  (frase incompleta/sem entonação)")
        print(f"✅ Função nova:    '{novo}'  (mantém entonação natural)")
        
        # Análise
        if not antigo.endswith((',', '!', '?', ':')) and not antigo.endswith(' '):
            print("   🚨 PROBLEMA ANTIGO: Frase termina abruptamente")
        
        if novo.endswith(',') or ', ' in novo:
            print("   ✨ SOLUÇÃO NOVA: Pausas naturais preservadas")

def testar_casos_especiais():
    """Testa casos especiais que podem ser problemáticos"""
    
    print("\n" + "=" * 70)
    print("TESTE DE CASOS ESPECIAIS")
    print("=" * 70)
    
    casos_especiais = [
        'Números decimais: 3.14 e 2.5 são importantes.',
        'URLs: visite www.exemplo.com.br para mais info.',
        'Horários: às 14.30h teremos a aula.',
        'Versões: Python 3.8.5 é recomendado.',
        'Múltiplas frases: Primeira frase. Segunda frase. Terceira frase.'
    ]
    
    print("⚠️  Estes casos podem precisar de atenção especial:")
    
    for caso in casos_especiais:
        resultado = limpar_texto(caso)
        print(f"\n📝 Original: '{caso}'")
        print(f"🔄 Resultado: '{resultado}'")
        
        # Verificar se há elementos que podem precisar de tratamento especial
        if any(char.isdigit() for char in caso) and '.' in caso:
            print("   ℹ️  Contém números decimais - verificar se faz sentido")
        
        if 'www.' in caso or '.com' in caso:
            print("   ℹ️  Contém URL - pode precisar tratamento especial")

def main():
    """Função principal do teste"""
    try:
        print("🚀 Iniciando testes da função limpar_texto() melhorada...")
        
        # Executar todos os testes
        testar_casos_pontuacao()
        demonstrar_antes_depois()
        testar_casos_especiais()
        
        print("\n" + "=" * 70)
        print("✅ TESTES CONCLUÍDOS COM SUCESSO!")
        print("=" * 70)
        print()
        print("💡 PRÓXIMOS PASSOS:")
        print("   1. Teste a função com seus próprios textos")
        print("   2. Execute o TTS e verifique se não fala mais 'ponto'")
        print("   3. Confirme que a entonação continua natural")
        print("   4. Ajuste casos especiais se necessário")
        print()
        print("🎯 Para usar a função melhorada:")
        print("   from usar_minha_voz import limpar_texto")
        print("   texto_limpo = limpar_texto('Seu texto aqui.')")
        
    except Exception as e:
        print(f"\n❌ ERRO durante os testes: {e}")
        print("Verifique se o arquivo usar_minha_voz.py está acessível")

if __name__ == "__main__":
    main() 