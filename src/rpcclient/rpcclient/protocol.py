from construct import Struct, Int32ul, PrefixedArray, Const, Enum, this, PascalString, Switch, PaddedString, Bytes, \
    Int64ul, Int8ul, IfThenElse, Float64l, Array, Union, Int16ul, Default

cmd_type_t = Enum(Int32ul,
                  CMD_EXEC=0,
                  CMD_DLOPEN=1,
                  CMD_DLCLOSE=2,
                  CMD_DLSYM=3,
                  CMD_CALL=4,
                  CMD_PEEK=5,
                  CMD_POKE=6,
                  CMD_REPLY_ERROR=7,
                  CMD_REPLY_PEEK=8,
                  CMD_GET_DUMMY_BLOCK=9,
                  CMD_CLOSE=10,
                  CMD_REPLY_POKE=11,
                  )

arch_t = Enum(Int32ul,
              ARCH_UNKNOWN=0,
              ARCH_ARM64=1,
              )

DEFAULT_PORT = 5910
SERVER_MAGIC_VERSION = 0x88888801
MAGIC = 0x12345678
MAX_PATH_LEN = 1024

protocol_handshake_t = Struct(
    'magic' / Int32ul,
    'arch' / arch_t,
    'sysname' / PaddedString(256, 'utf8'),
)

cmd_exec_t = Struct(
    'background' / Int8ul,
    'argv' / PrefixedArray(Int32ul, PascalString(Int32ul, 'utf8')),
    'envp' / PrefixedArray(Int32ul, PascalString(Int32ul, 'utf8')),
)

cmd_dlopen_t = Struct(
    'filename' / PaddedString(MAX_PATH_LEN, 'utf8'),
    'mode' / Int32ul,
)

cmd_dlclose_t = Struct(
    'lib' / Int64ul,
)

cmd_dlsym_t = Struct(
    'lib' / Int64ul,
    'symbol_name' / PaddedString(MAX_PATH_LEN, 'utf8'),
)

argument_type_t = Enum(Int64ul,
                       Integer=0,
                       Double=1)

argument_t = Struct(
    'type' / argument_type_t,
    'value' / IfThenElse(this.type == argument_type_t.Integer, Int64ul, Float64l),
)

cmd_call_t = Struct(
    'address' / Int64ul,
    'argv' / PrefixedArray(Int64ul, argument_t),
)

cmd_peek_t = Struct(
    'address' / Int64ul,
    'size' / Int64ul,
)

cmd_poke_t = Struct(
    'address' / Int64ul,
    'size' / Int64ul,
    'data' / Bytes(this.size),
)

protocol_message_t = Struct(
    'magic' / Const(MAGIC, Int32ul),
    'port' / Default(Int32ul, 0),
    'cmd_type' / cmd_type_t,
    'data' / Switch(this.cmd_type, {
        cmd_type_t.CMD_EXEC: cmd_exec_t,
        cmd_type_t.CMD_DLOPEN: cmd_dlopen_t,
        cmd_type_t.CMD_DLCLOSE: cmd_dlclose_t,
        cmd_type_t.CMD_DLSYM: cmd_dlsym_t,
        cmd_type_t.CMD_CALL: cmd_call_t,
        cmd_type_t.CMD_PEEK: cmd_peek_t,
        cmd_type_t.CMD_POKE: cmd_poke_t,
    })
)

reply_protocol_message_t = Struct(
    'magic' / Const(MAGIC, Int32ul),
    'cmd_type' / cmd_type_t,
)

exec_chunk_type_t = Enum(Int32ul,
                         CMD_EXEC_CHUNK_TYPE_STDOUT=0,
                         CMD_EXEC_CHUNK_TYPE_ERRORCODE=1,
                         )

exec_chunk_t = Struct(
    'chunk_type' / exec_chunk_type_t,
    'size' / Int32ul,
)

return_registers_arm_t = Struct(
    'x' / Array(8, Int64ul),
    'd' / Array(8, Float64l),
)

call_response_t_size = 128

call_response_t = Struct(
    'return_values' / Union(None,
                            'arm_registers' / return_registers_arm_t,
                            'return_value' / Int64ul,
                            ),
)

dummy_block_t = Int64ul
