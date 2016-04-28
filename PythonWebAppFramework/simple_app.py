# coding=utf-8
"""
WSGI中规定：application是一个 可调用对象（callable object），它接受 environ 和 start_response 两个参数，并返回一个 字符串迭代对象。

其中，可调用对象 包括 函数、方法、类 或者 具有__call__方法的 实例；environ 是一个字典对象，包括CGI风格的环境变量（CGI-style environment variables）和 WSGI必需的变量（WSGI-required variables）；start_response 是一个可调用对象，它接受两个 常规参数（status，response_headers）和 一个 默认参数（exc_info）；字符串迭代对象 可以是 字符串列表、生成器函数 或者 具有__iter__方法的可迭代实例。更多细节参考 Specification Details。

The Application/Framework Side 中给出了一个典型的application实现：
"""
def simple_app(environ, start_response, exc_info=None):
    status = '200 OK'
    response_header = [
        ('Content-type', 'text/plain'),
    ]
    start_response(status, response_header)
    return ['Saluton!\n']           # windows环境下可能需要将string转换为bytes type