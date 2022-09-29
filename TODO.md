# Todo-List

+ ~~Achieve 150 commits~~
+ Fix map_position breaking when turning around
    (i.e. add smart position detection)

+ Try and decode new message types
    + battery level (C2V & V2C)
    + road center offset update (V2C)
    + delocalization (V2C)
    + ping (C2V &V2C)
    + try and rediscover setLights and setEngineLights based on another library

+ Write a Documentation
+ Find out what piece value 66 is

## pep-up
+ ~~Change all to snake case~~
    ~~Implement aliases with `DeprecationWarning`~~
+ ~~rename `Vehicle.__notify_handler__`~~
+ ~~rename all `[...]Exception`s to `[...]Error`s~~
    ~~Implement deprecated aliases here as well~~ (Implemented as regular aliases)
+ rename `anki.utility` and `anki.utility.util` since they don't actually provide any
+ ~~Change the `raise` usages to `raise from`~~