import pytube
from pytube import YouTube
import os
import sys
from pydub import AudioSegment
import re

def corrigir_erro_cipher():
    # Correção para o erro de cipher
    from pytube import cipher
    from pytube.cipher import get_initial_function_name as get_initial_function_name_original

    def get_initial_function_name(js):
        try:
            return get_initial_function_name_original(js)
        except:
            # Fallback para quando o método original falha
            pattern = r'(?:\b[cs]\s*&&\s*[adf]\.set\([^,]+\s*,\s*encodeURIComponent\s*\(\s*)([^(]+)(?:\s*\('
            result = re.search(pattern, js)
            if not result:
                raise Exception("Não foi possível encontrar a função inicial")
            return result.group(1)

    cipher.get_initial_function_name = get_initial_function_name

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

def mostrar_menu():
    print("\n=== YouTube Downloader ===")
    print("1. Baixar Vídeo")
    print("2. Baixar Apenas Áudio")
    print("3. Sair")
    return input("\nEscolha uma opção (1-3): ")

def escolher_formato_video():
    print("\nEscolha o formato do vídeo:")
    print("1. MP4")
    print("2. AVI")
    return input("\nEscolha uma opção (1-2): ")

def escolher_formato_audio():
    print("\nEscolha o formato do áudio:")
    print("1. MP3")
    print("2. WAV")
    return input("\nEscolha uma opção (1-2): ")

def extrair_video_id(url):
    # Padrões para URLs do YouTube
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',  # Videos normais
        r'(?:shorts\/)([0-9A-Za-z_-]{11}).*'  # Shorts
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def baixar_video(url, apenas_audio=False):
    try:
        # Aplicar correção para o erro cipher
        corrigir_erro_cipher()
        
        # Verificar e corrigir a URL
        video_id = extrair_video_id(url)
        if not video_id:
            print("\nURL inválida! Certifique-se de que é uma URL válida do YouTube.")
            return
            
        url = f"https://www.youtube.com/watch?v={video_id}"
        
        # Tentar criar objeto YouTube com várias tentativas
        tentativas = 3
        for tentativa in range(tentativas):
            try:
                yt = YouTube(url)
                break
            except Exception as e:
                if tentativa == tentativas - 1:
                    raise e
                print(f"\nTentativa {tentativa + 1} falhou. Tentando novamente...")
                continue

        print(f"\nBaixando: {yt.title}")

        if apenas_audio:
            formato = escolher_formato_audio()
            # Primeiro baixamos em MP4 e depois convertemos
            stream = yt.streams.filter(only_audio=True).first()
            if not stream:
                raise Exception("Nenhum stream de áudio encontrado")
                
            arquivo_baixado = stream.download()
            
            # Convertendo para o formato escolhido
            nome_base = os.path.splitext(arquivo_baixado)[0]
            if formato == "1":  # MP3
                AudioSegment.from_file(arquivo_baixado).export(
                    f"{nome_base}.mp3", format="mp3")
                os.remove(arquivo_baixado)  # Remove o arquivo MP4 original
                print(f"\nÁudio baixado com sucesso como MP3!")
            else:  # WAV
                AudioSegment.from_file(arquivo_baixado).export(
                    f"{nome_base}.wav", format="wav")
                os.remove(arquivo_baixado)  # Remove o arquivo MP4 original
                print(f"\nÁudio baixado com sucesso como WAV!")
        else:
            formato = escolher_formato_video()
            if formato == "1":  # MP4
                stream = yt.streams.filter(progressive=True, file_extension="mp4").order_by("resolution").desc().first()
                if not stream:
                    raise Exception("Nenhum stream de vídeo encontrado")
                stream.download()
                print("\nVídeo baixado com sucesso como MP4!")
            else:  # AVI
                stream = yt.streams.filter(progressive=True, file_extension="mp4").order_by("resolution").desc().first()
                if not stream:
                    raise Exception("Nenhum stream de vídeo encontrado")
                arquivo_baixado = stream.download()
                nome_base = os.path.splitext(arquivo_baixado)[0]
                os.system(f'ffmpeg -i "{arquivo_baixado}" "{nome_base}.avi"')
                os.remove(arquivo_baixado)
                print("\nVídeo baixado com sucesso como AVI!")

    except Exception as e:
        print(f"\nErro ao baixar: {str(e)}")
        print("Dicas de solução:")
        print("1. Verifique sua conexão com a internet")
        print("2. Certifique-se de que o vídeo está disponível (não é privado ou restrito)")
        print("3. Tente novamente em alguns minutos")
        print("4. Se o problema persistir, tente atualizar o pytube:")
        print("   pip install --upgrade pytube")

def main():
    while True:
        limpar_tela()
        opcao = mostrar_menu()

        if opcao == "3":
            print("\nSaindo do programa...")
            sys.exit()

        if opcao in ["1", "2"]:
            url = input("\nDigite a URL do vídeo do YouTube (incluindo shorts): ")
            baixar_video(url, apenas_audio=(opcao == "2"))
            input("\nPressione ENTER para continuar...")
        else:
            print("\nOpção inválida!")
            input("\nPressione ENTER para continuar...")

if __name__ == "__main__":
    main() 