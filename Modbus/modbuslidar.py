from pymodbus.client import ModbusSerialClient
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian

#Configurando a comunicacao
PORTA_SERIAL = 
BAUDRATE =
PARIDADE = ''
STOP_BITS =
BYTESIZE =
ID_ESCRAVO =

#Criando o cliente Modbus RTU
client = ModbusSerialClient(
    port = PORTA_SERIAL,
    baudrate = BAUDRATE,
    parity = PARIDADE,
    stopbits = STOP_BITS,
    bytesize = BYTESIZE
    timeout = 0.5
)
print('Tentando se conectar ao lidar...')

#tTentando estabelecer a conexao
if client.connect():
    print('Conexao estabelecida com sucesso')
    try:
        endereco_registrador = 
        numero_de_registradores = 
        print(f"Requisitando {numero_de_registradores} registradores a partir do endereço {endereco_registrador}...")
        resultado = client.read_holding_registers(
            adresss = endereco_registrador,
            count = numero_de_registradores,
            slave = ID_ESCRAVO
        )
        if not resultado.isError():
            print('Resposta recebida do lidar')
            decoder = BinaryPayloadDecoder.fromRegisters(
                resultado.registers,
                byteorder = Endian.Big
                wordorder = Endian.Little
                )
            valor_decodificado = decoder.decode_32bit_float()
            print(f'Valor Bruto nos Registradores: {resultado.registers}')
            print(f"Valor Decodificado (Float 32 bits): {valor_decodificado:.2f}")
        else:
            print(f'Erro ao ler os registradores: {resultado}')
    finally: 
        client.close()
else:
    print('Nao foi possivel se conectar ao lidar')
