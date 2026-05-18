import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

# Driver nome usual para quando se direciona, "dirige o navegador"
@pytest.fixture(scope="module")
def driver():

    # abrir um vez tudo
    opcoes = Options()
    # faz não precisar abrir janela - aqui abre em segundo plano
    opcoes.add_argument("--headless")
    # para github actions
    opcoes.add_argument("--no-sandbox")
    # para  não ter erros de memória
    opcoes.add_argument("--disable-dev-shm-usage")
    # configuira tamanho da tela
    opcoes.add_argument("--window-size=1280,720")

    servico = Service()
    navegador = webdriver.Chrome(service=servico, options=opcoes)

    yield navegador

    #_____ Teardown - fecha o navegador após os testes
    navegador.quit()


BASE_URL = "http://localhost:5000"
# segundos
TIMEOUT  = 10


def esperar_visualizacao_elemento(driver, by, valor, timeout=TIMEOUT):

    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((by, valor))
    )


#_______________ Teste

class TestE2ECompra:

    # vê se carrega o title do html
    def test_pag_carregar_titulo(self, driver):
 
        driver.get(BASE_URL)
        assert "GeekStore" in driver.title or "GeekStore" in driver.page_source

    def test_selecionar_produtos_id(self, driver):

        driver.get(BASE_URL)
        elemento_selecionado = esperar_visualizacao_elemento(driver, By.ID, "produto_id")
        assert elemento_selecionado is not None

    def test_selecionar_opcoes(self, driver):
        
        driver.get(BASE_URL)
        elemento_selecionado = esperar_visualizacao_elemento(driver, By.ID, "produto_id")
        select = Select(elemento_selecionado)
        assert len(select.options) > 0

    def test_comprar_sem_cupom(self, driver):

        # abre a pag
        driver.get(BASE_URL)

        # Seleciona o produto, que no caso é o 2/mangá
        elemento_selecionado = esperar_visualizacao_elemento(driver, By.ID, "produto_id")
        Select(elemento_selecionado).select_by_index(2)

        # Define quantidade
        campo_qtd = driver.find_element(By.ID, "quantidade")
        campo_qtd.clear()
        campo_qtd.send_keys("1")

        # Seleciona btn comprar
        botao = driver.find_element(By.ID, "btn-comprar")
        botao.click()

        mensagem_div = esperar_visualizacao_elemento(driver, By.ID, "mensagem-resultado")

        assert "Compra efetuada" in mensagem_div.text or "sucesso" in mensagem_div.text.lower()

    def test_comprar_com_cupom(self, driver):
      
        driver.get(BASE_URL)

        elemento_selecionado = esperar_visualizacao_elemento(driver, By.ID, "produto_id")
        Select(elemento_selecionado).select_by_index(2)

        campo_qtd = driver.find_element(By.ID, "quantidade")
        campo_qtd.clear()
        campo_qtd.send_keys("1")

        # Seleciona o cupom
        campo_cupom = driver.find_element(By.ID, "cupom")
        campo_cupom.clear()
        campo_cupom.send_keys("DESCONTO10")

        driver.find_element(By.ID, "btn-comprar").click()

        mensagem_div = esperar_visualizacao_elemento(driver, By.ID, "mensagem-resultado")
        assert "Compra realizada" in mensagem_div.text or "sucesso" in mensagem_div.text.lower()

    def test_comprar_sem_estoque(self, driver):

        driver.get(BASE_URL)

        elemento_selecionado = esperar_visualizacao_elemento(driver, By.ID, "produto_id")
        # no caso há 0 produtos
        # lembrando que [1] da tabela é id, o índice é 1 
        Select(elemento_selecionado).select_by_index(1)

        driver.find_element(By.ID, "btn-comprar").click()

        mensagem_div = esperar_visualizacao_elemento(driver, By.ID, "mensagem-resultado")
        texto = mensagem_div.text.lower()
        assert "insuficiente" in texto or "estoque" in texto or "erro" in texto


'''
ordem importa

Tabela
indice  id
[0]    [1] - Lego One Piece, Tenda Palhaço Buggy - Modelo 3D - 573 peças,  480.00, 5
[1]    [2] - Cartucho Road Rash 2, preco=69.94, estoque=0
[2]    [3] - Mangá DanDaDan, vol 1, 36.89, 10
[3]    [4] - Boneco Colecionável, Hisoka Morow - 33cm, Hunter X Hunter, 977.00, 3

'''