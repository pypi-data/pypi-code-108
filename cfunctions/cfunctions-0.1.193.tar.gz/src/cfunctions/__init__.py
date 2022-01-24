'''
# CFunctions

CFunctions (cloud functions, compute functions, construct functions) are a
building block of the [constructs programming model] which can be used to
package JavaScript code and run it on a cloud system.

Let's take a look at a simple CFunction:

```python
const { CFunction } = require('cfunctions');

const cfunc = new CFunction({
  capture: [ 'x', 'y' ],
  code: 'x + y'
});

console.log('outfile:', cfunc.outfile);
console.log('env:', cfunc.env);
```

The output will look like this:

```shell
outfile: /tmp/.cf.out.TAJEO8/cf.js
env: { __CF__x__: '100', __CF__y__: '200' }
```

The `cf.js` file is a a self-contained JavaScript module which can be loaded
through a `require()` statement and returns an async function that executes the
code after binding it from a set of environment variables.

Let's execute our cfunction:

```shell
$ export __CF__x__=123
$ export __CF__y__=10
$ node -e "require('/tmp/.cf.out.TAJEO8/cf.js')().then(result => console.log(result))"
12310
```

The `CFunction.exec()` static method can also be used to execute the function:

```js
const result = CFunction.exec('/tmp/.cf.out.TAJEO8/cf.js', {
  env: {
    __CF__x__: 123,
    __CF__y__: 10
  }
});

console.log(result);
```

## License

Licensed under the [Apache 2.0](./LICENSE) license.
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from ._jsii import *


class CFunction(metaclass=jsii.JSIIMeta, jsii_type="cfunctions.CFunction"):
    def __init__(
        self,
        *,
        capture: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        code: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param capture: Symbols to capture.
        :param code: Javascript code to execute. Default: "true;"
        '''
        props = CFunctionProps(capture=capture, code=code)

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="exec") # type: ignore[misc]
    @builtins.classmethod
    def exec(
        cls,
        file: builtins.str,
        *,
        env: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> typing.Any:
        '''
        :param file: -
        :param env: Environment variables to bind to the child process. You can use ``cfunction.env`` to bind the original symbols. Default: {}
        '''
        options = ExecOptions(env=env)

        return typing.cast(typing.Any, jsii.sinvoke(cls, "exec", [file, options]))

    @jsii.member(jsii_name="toJson")
    def to_json(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.invoke(self, "toJson", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="env")
    def env(self) -> typing.Mapping[builtins.str, builtins.str]:
        '''Environment variables that are expected to be available when the function is executed.'''
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "env"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="outfile")
    def outfile(self) -> builtins.str:
        '''The location of the function bundle (.js file).'''
        return typing.cast(builtins.str, jsii.get(self, "outfile"))


@jsii.data_type(
    jsii_type="cfunctions.CFunctionProps",
    jsii_struct_bases=[],
    name_mapping={"capture": "capture", "code": "code"},
)
class CFunctionProps:
    def __init__(
        self,
        *,
        capture: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        code: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param capture: Symbols to capture.
        :param code: Javascript code to execute. Default: "true;"
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if capture is not None:
            self._values["capture"] = capture
        if code is not None:
            self._values["code"] = code

    @builtins.property
    def capture(self) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''Symbols to capture.'''
        result = self._values.get("capture")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def code(self) -> typing.Optional[builtins.str]:
        '''Javascript code to execute.

        :default: "true;"
        '''
        result = self._values.get("code")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CFunctionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cfunctions.ExecOptions",
    jsii_struct_bases=[],
    name_mapping={"env": "env"},
)
class ExecOptions:
    def __init__(
        self,
        *,
        env: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''
        :param env: Environment variables to bind to the child process. You can use ``cfunction.env`` to bind the original symbols. Default: {}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if env is not None:
            self._values["env"] = env

    @builtins.property
    def env(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Environment variables to bind to the child process.

        You can use ``cfunction.env`` to bind the original symbols.

        :default: {}
        '''
        result = self._values.get("env")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ExecOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CFunction",
    "CFunctionProps",
    "ExecOptions",
]

publication.publish()
