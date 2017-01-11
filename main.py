import sys

class InvalidCommand(Exception):
    def __init__(self, cmd):
        super(InvalidCommand, self).__init__("Invalid command %s" % repr(cmd))

class UnknownComponent(Exception):
    def __init__(self, comp):
        super(UnknownComponent, self).__init__("Unknonwn component %s" % repr(comp))

class FailedInstallationDependency(Exception):
    def __init__(self, comp, deps):
        super(FailedInstallationDependency, self).__init__("Could not install %s due to failed dependency %s" % (repr(comp), repr(deps)))


# comp dependcy table [name] = obj
COMPONENT_TABLE = dict()   

# CMDS
CMD_DEPENDS = "DEPEND"
CMD_INSTALL = "INSTALL"
CMD_REMOVE = "REMOVE" 
CMD_LIST = "LIST"
CMDS = (CMD_DEPENDS, CMD_INSTALL, CMD_REMOVE, CMD_LIST)


class ComponentItem:
    def __init__(self, name):
        self.name = name
        self._depends_on = set()
        self._depended_by= set()
        self.installed = False

    def add_depends_on(self, itemname):
        self._depends_on.add(itemname)

    def add_depended_by(self, itemname):
        self._depended_by.add(itemname)

    def install(self):
        if self.installed:
            print "%s already installed" % (self.name)
            return

        print "Installing : " + self.name
        for d in self._depends_on:
            dcomp = COMPONENT_TABLE[d]
            if not dcomp.installed:
                print "Installing dependency %s for %s : " % (repr(d), self.name)
                dcomp.install()
        self.installed = True

    def remove(self):
        if not self.installed:
            print "%s is not installed" % (self.name)
            return

        for d in self._depended_by:
            dcomp = COMPONENT_TABLE[d.name]
            if dcomp.installed:
                print "Removing dependency %s for %s : " % (repr(d), self.name)
                dcomp.remove()
        self.installed = False

    def __repr__(self):
        return "Name: " + self.name + " DependsOn: " + repr(self._depends_on) + " DependedBy: " + repr(self._depended_by)


def dependHandler(items):
    t = items[0]
    deps = items[1:]

    target = COMPONENT_TABLE.get(t, None)
    if target is None:
            target = ComponentItem(t)
            COMPONENT_TABLE[t] = target

    for d in deps:
        print "D: " + d
        dcomp = COMPONENT_TABLE.get(d, None)
        if dcomp is None:
            dcomp = ComponentItem(d)
            COMPONENT_TABLE[d] = dcomp
        target.add_depends_on(d)
        dcomp.add_depended_by(target)

    print "Dependencies:"
    for i in items:
        print COMPONENT_TABLE[i]



def installHandler(items):
    for i in  items:
        comp = COMPONENT_TABLE.get(i, None)
        if comp is None:
            raise UnknownComponent(i)
        comp.install()

def removeHandler(items):
    for i in  items:
        print "Removing :" + i

        comp = COMPONENT_TABLE.get(i, None)
        if comp is None:
            raise UnknownComponent(i)
        comp.remove()

def listHandler(items):
    print "Installed components:"
    for c in COMPONENT_TABLE.values():
        if c.installed:
            print "    %s" % c.name

CMD_HANDLER_TABLE = {
    CMD_DEPENDS: dependHandler,
    CMD_INSTALL: installHandler,
    CMD_REMOVE: removeHandler,
    CMD_LIST: listHandler
}

       


def parseInput(indata):
    d = indata.split()
    cmd = d[0]
    items = d[1:]
    return cmd, items

def readInput(filepath):
    with open(filepath) as f:
        inputlines = f.readlines()

    for inputline in inputlines:
        cmd, items = parseInput(inputline.strip())
        if cmd not in CMDS:
            raise InvalidCommand(cmd)

        try:
            CMD_HANDLER_TABLE[cmd](items)
        except UnknownComponent as u:
            print (u)

if __name__ == '__main__':
    readInput("./inputfile.txt")
