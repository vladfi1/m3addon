#!/usr/bin/python3
# -*- coding: utf-8 -*-
""" 
IMPORTANT: This is a automatically generated file. 
IMPORTANT: Do not modify!
"""
import struct
from sys import stderr

class NoSuchAttributeException(Exception):
    def __init__(self, attribute):
        super(Exception, self).__init__("%s is not a known attribute." % attribute)
        
class UnexpectedTagException(Exception):
    def __init__(self, tagName):
        pass

def unpackTag(s):
    if s[3] == 0:
        return chr(s[2]) + chr(s[1]) + chr(s[0])
    else:
        return chr(s[3]) + chr(s[2]) + chr(s[1]) + chr(s[0])

def packTag(s):
    if len(s) == 4:
        return (s[3] + s[2] + s[1] + s[0]).encode("ascii")
    else:
        return (s[2] + s[1] + s[0]).encode("ascii") + b"\x00"

def increaseToValidSectionSize(size):
    blockSize = 16
    incompleteBlockBytes = (size % blockSize)
    if incompleteBlockBytes != 0:
        missingBytesToCompleteBlock = blockSize - incompleteBlockBytes
        return size + missingBytesToCompleteBlock
    else:
        return size
            
def byteDataToHex(byteData):
    s = "0x"
    for i in range(len(byteData)):
        hexValue = hex(byteData[i])[2:]
        if len(hexValue) <= 1:
            hexValue = "0"+hexValue
        s +=hexValue
    return s
    
class Section:
    """Has fields indexEntry and contentClass and sometimes also the fields rawBytes and content """
    
    def __init__(self):
        self.timesReferenced = 0
    
    def determineContentField(self):
        indexEntry = self.indexEntry
        self.content = self.contentClass.createInstances(rawBytes=self.rawBytes, count=indexEntry.repetitions)

    def determineFieldRawBytes(self):
        minRawBytes = self.contentClass.rawBytesForOneOrMore(oneOrMore=self.content)
        sectionSize = increaseToValidSectionSize(len(minRawBytes))
        if len(minRawBytes) == sectionSize:
            self.rawBytes = minRawBytes
        else:
            rawBytes = bytearray(sectionSize)
            rawBytes[0:len(minRawBytes)] = minRawBytes
            for i in range(len(minRawBytes),sectionSize):
                rawBytes[i] = 0xaa
            self.rawBytes = rawBytes
    def resolveReferences(self, sections):
        self.contentClass.resolveReferencesOfOneOrMore(self.content, sections)

class FieldTypeInfo:
    """ Stores information of the type of a field:"""
    def __init__(self, typeName, typeClass, isList):
        self.typeName = typeName
        self.typeClass = typeClass
        self.isList = isList

def resolveRef(ref, sections, expectedType, variable):
    if ref.entries == 0:
        if expectedType == None:
            return []
        else:
            return expectedType.createEmptyArray()
    
    referencedSection = sections[ref.index]
    referencedSection.timesReferenced += 1
    indexEntry = referencedSection.indexEntry
    
    if indexEntry.repetitions < ref.entries:
        raise Exception("%s references more elements then there actually are" % variable)

    referencedObject = referencedSection.content
    if expectedType != None:
        expectedTagName = expectedType.tagName
        actualTagName = indexEntry.tag
        if actualTagName != expectedTagName:
            raise Exception("Expected ref %s point to %s, but it points to %s" % (variable, expectedTagName, actualTagName))
        expectedTagVersion = expectedType.tagVersion
        actualTagVersion = indexEntry.version
        if actualTagName != expectedTagName:
            raise Exception("Expected ref %s point to %s in version %s, but it points version %s" % (variable, expectedTagName,expectedTagVersion, actualTagVersion))

    else:
        raise Exception("Field %s can be marked as a reference pointing to %sV%s" % (variable, indexEntry.tag,indexEntry.version))
    return referencedObject


class Reference:
    """A reference to one or more entries in a file"""
    tagName = "Reference"
    size = 12
    structFormat = struct.Struct("<III")
    fields = ["entries", "index", "flags"]

    def __setattr__(self, name, value):
        if name in ["entries", "index", "flags"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["entries", "index", "flags"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        pass #nothing to do
    
    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        pass #nothing to do

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert Reference.size == Reference.structFormat.size
            rawBytes = readable.read(Reference.size)
        if rawBytes != None:
            l = Reference.structFormat.unpack(rawBytes)
            self.entries = l[0]
            self.index = l[1]
            self.flags = l[2]
        if (readable == None) and (rawBytes == None):
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + Reference.size
        for i in range(count):
            list.append(Reference(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += Reference.size
        return list
    
    def toBytes(self):
        return Reference.structFormat.pack(self.entries, self.index, self.flags)
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(Reference.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = Reference.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += Reference.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return Reference.countOneOrMore(object) * Reference.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"index": {}, "flags": {}, "entries": {}}
    
    def getNamedBit(self, field, bitName):
        mask = Reference.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = Reference.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return Reference.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"entries":FieldTypeInfo("uint32",None, False), "index":FieldTypeInfo("uint32",None, False), "flags":FieldTypeInfo("uint32",None, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return Reference.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != Reference:
            raise Exception("%s is not of type %s but %s" % (id, "Reference", type(instance)))
        fieldId = id + ".entries"

        if (type(instance.entries) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".index"

        if (type(instance.index) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".flags"

        if (type(instance.flags) != int):
            raise Exception("%s is not an int" % (fieldId))


class SmallReference:
    """A reference to one or more entries in a file"""
    tagName = "SmallReference"
    size = 8
    structFormat = struct.Struct("<II")
    fields = ["entries", "index"]

    def __setattr__(self, name, value):
        if name in ["entries", "index"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["entries", "index"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        pass #nothing to do
    
    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        pass #nothing to do

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert SmallReference.size == SmallReference.structFormat.size
            rawBytes = readable.read(SmallReference.size)
        if rawBytes != None:
            l = SmallReference.structFormat.unpack(rawBytes)
            self.entries = l[0]
            self.index = l[1]
        if (readable == None) and (rawBytes == None):
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + SmallReference.size
        for i in range(count):
            list.append(SmallReference(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += SmallReference.size
        return list
    
    def toBytes(self):
        return SmallReference.structFormat.pack(self.entries, self.index)
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(SmallReference.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = SmallReference.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += SmallReference.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return SmallReference.countOneOrMore(object) * SmallReference.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"index": {}, "entries": {}}
    
    def getNamedBit(self, field, bitName):
        mask = SmallReference.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = SmallReference.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return SmallReference.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"entries":FieldTypeInfo("uint32",None, False), "index":FieldTypeInfo("uint32",None, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return SmallReference.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != SmallReference:
            raise Exception("%s is not of type %s but %s" % (id, "SmallReference", type(instance)))
        fieldId = id + ".entries"

        if (type(instance.entries) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".index"

        if (type(instance.index) != int):
            raise Exception("%s is not an int" % (fieldId))


class VEC2V0:
    """A Vector with 2 components"""
    fullName = "VEC2V0"
    tagName = "VEC2"
    tagVersion = 0
    size = 8
    structFormat = struct.Struct("<ff")
    fields = ["x", "y"]

    def __setattr__(self, name, value):
        if name in ["x", "y"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["x", "y"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        pass #nothing to do
    
    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        pass #nothing to do

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert VEC2V0.size == VEC2V0.structFormat.size
            rawBytes = readable.read(VEC2V0.size)
        if rawBytes != None:
            l = VEC2V0.structFormat.unpack(rawBytes)
            self.x = l[0]
            self.y = l[1]
        if (readable == None) and (rawBytes == None):
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + VEC2V0.size
        for i in range(count):
            list.append(VEC2V0(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += VEC2V0.size
        return list
    
    def toBytes(self):
        return VEC2V0.structFormat.pack(self.x, self.y)
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(VEC2V0.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = VEC2V0.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += VEC2V0.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return VEC2V0.countOneOrMore(object) * VEC2V0.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"y": {}, "x": {}}
    
    def getNamedBit(self, field, bitName):
        mask = VEC2V0.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = VEC2V0.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return VEC2V0.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"x":FieldTypeInfo("float",None, False), "y":FieldTypeInfo("float",None, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return VEC2V0.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != VEC2V0:
            raise Exception("%s is not of type %s but %s" % (id, "VEC2V0", type(instance)))
        fieldId = id + ".x"

        if (type(instance.x) != float):
            raise Exception("%s is not a float" % (fieldId))
        fieldId = id + ".y"

        if (type(instance.y) != float):
            raise Exception("%s is not a float" % (fieldId))


class VEC3V0:
    """A Vector with 3 components"""
    fullName = "VEC3V0"
    tagName = "VEC3"
    tagVersion = 0
    size = 12
    structFormat = struct.Struct("<fff")
    fields = ["x", "y", "z"]

    def __setattr__(self, name, value):
        if name in ["x", "y", "z"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["x", "y", "z"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        pass #nothing to do
    
    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        pass #nothing to do

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert VEC3V0.size == VEC3V0.structFormat.size
            rawBytes = readable.read(VEC3V0.size)
        if rawBytes != None:
            l = VEC3V0.structFormat.unpack(rawBytes)
            self.x = l[0]
            self.y = l[1]
            self.z = l[2]
        if (readable == None) and (rawBytes == None):
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + VEC3V0.size
        for i in range(count):
            list.append(VEC3V0(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += VEC3V0.size
        return list
    
    def toBytes(self):
        return VEC3V0.structFormat.pack(self.x, self.y, self.z)
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(VEC3V0.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = VEC3V0.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += VEC3V0.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return VEC3V0.countOneOrMore(object) * VEC3V0.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"y": {}, "x": {}, "z": {}}
    
    def getNamedBit(self, field, bitName):
        mask = VEC3V0.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = VEC3V0.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return VEC3V0.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"x":FieldTypeInfo("float",None, False), "y":FieldTypeInfo("float",None, False), "z":FieldTypeInfo("float",None, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return VEC3V0.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != VEC3V0:
            raise Exception("%s is not of type %s but %s" % (id, "VEC3V0", type(instance)))
        fieldId = id + ".x"

        if (type(instance.x) != float):
            raise Exception("%s is not a float" % (fieldId))
        fieldId = id + ".y"

        if (type(instance.y) != float):
            raise Exception("%s is not a float" % (fieldId))
        fieldId = id + ".z"

        if (type(instance.z) != float):
            raise Exception("%s is not a float" % (fieldId))


class VEC4V0:
    """A Vector with 4 components"""
    fullName = "VEC4V0"
    tagName = "VEC4"
    tagVersion = 0
    size = 16
    structFormat = struct.Struct("<ffff")
    fields = ["x", "y", "z", "w"]

    def __setattr__(self, name, value):
        if name in ["x", "y", "z", "w"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["x", "y", "z", "w"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        pass #nothing to do
    
    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        pass #nothing to do

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert VEC4V0.size == VEC4V0.structFormat.size
            rawBytes = readable.read(VEC4V0.size)
        if rawBytes != None:
            l = VEC4V0.structFormat.unpack(rawBytes)
            self.x = l[0]
            self.y = l[1]
            self.z = l[2]
            self.w = l[3]
        if (readable == None) and (rawBytes == None):
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + VEC4V0.size
        for i in range(count):
            list.append(VEC4V0(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += VEC4V0.size
        return list
    
    def toBytes(self):
        return VEC4V0.structFormat.pack(self.x, self.y, self.z, self.w)
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(VEC4V0.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = VEC4V0.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += VEC4V0.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return VEC4V0.countOneOrMore(object) * VEC4V0.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"y": {}, "x": {}, "z": {}, "w": {}}
    
    def getNamedBit(self, field, bitName):
        mask = VEC4V0.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = VEC4V0.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return VEC4V0.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"x":FieldTypeInfo("float",None, False), "y":FieldTypeInfo("float",None, False), "z":FieldTypeInfo("float",None, False), "w":FieldTypeInfo("float",None, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return VEC4V0.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != VEC4V0:
            raise Exception("%s is not of type %s but %s" % (id, "VEC4V0", type(instance)))
        fieldId = id + ".x"

        if (type(instance.x) != float):
            raise Exception("%s is not a float" % (fieldId))
        fieldId = id + ".y"

        if (type(instance.y) != float):
            raise Exception("%s is not a float" % (fieldId))
        fieldId = id + ".z"

        if (type(instance.z) != float):
            raise Exception("%s is not a float" % (fieldId))
        fieldId = id + ".w"

        if (type(instance.w) != float):
            raise Exception("%s is not a float" % (fieldId))


class QUATV0:
    """A Quaternion """
    fullName = "QUATV0"
    tagName = "QUAT"
    tagVersion = 0
    size = 16
    structFormat = struct.Struct("<ffff")
    fields = ["x", "y", "z", "w"]

    def __setattr__(self, name, value):
        if name in ["x", "y", "z", "w"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["x", "y", "z", "w"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        pass #nothing to do
    
    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        pass #nothing to do

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert QUATV0.size == QUATV0.structFormat.size
            rawBytes = readable.read(QUATV0.size)
        if rawBytes != None:
            l = QUATV0.structFormat.unpack(rawBytes)
            self.x = l[0]
            self.y = l[1]
            self.z = l[2]
            self.w = l[3]
        if (readable == None) and (rawBytes == None):
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + QUATV0.size
        for i in range(count):
            list.append(QUATV0(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += QUATV0.size
        return list
    
    def toBytes(self):
        return QUATV0.structFormat.pack(self.x, self.y, self.z, self.w)
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(QUATV0.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = QUATV0.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += QUATV0.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return QUATV0.countOneOrMore(object) * QUATV0.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"y": {}, "x": {}, "z": {}, "w": {}}
    
    def getNamedBit(self, field, bitName):
        mask = QUATV0.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = QUATV0.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return QUATV0.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"x":FieldTypeInfo("float",None, False), "y":FieldTypeInfo("float",None, False), "z":FieldTypeInfo("float",None, False), "w":FieldTypeInfo("float",None, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return QUATV0.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != QUATV0:
            raise Exception("%s is not of type %s but %s" % (id, "QUATV0", type(instance)))
        fieldId = id + ".x"

        if (type(instance.x) != float):
            raise Exception("%s is not a float" % (fieldId))
        fieldId = id + ".y"

        if (type(instance.y) != float):
            raise Exception("%s is not a float" % (fieldId))
        fieldId = id + ".z"

        if (type(instance.z) != float):
            raise Exception("%s is not a float" % (fieldId))
        fieldId = id + ".w"

        if (type(instance.w) != float):
            raise Exception("%s is not a float" % (fieldId))


class Matrix44:
    """A 4x4 Matrix"""
    tagName = "Matrix44"
    size = 64
    structFormat = struct.Struct("<16s16s16s16s")
    fields = ["x", "y", "z", "w"]

    def __setattr__(self, name, value):
        if name in ["x", "y", "z", "w"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["x", "y", "z", "w"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        pass #nothing to do
    
    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        pass #nothing to do

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert Matrix44.size == Matrix44.structFormat.size
            rawBytes = readable.read(Matrix44.size)
        if rawBytes != None:
            l = Matrix44.structFormat.unpack(rawBytes)
            self.x = VEC4V0(rawBytes=l[0])
            self.y = VEC4V0(rawBytes=l[1])
            self.z = VEC4V0(rawBytes=l[2])
            self.w = VEC4V0(rawBytes=l[3])
        if (readable == None) and (rawBytes == None):
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + Matrix44.size
        for i in range(count):
            list.append(Matrix44(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += Matrix44.size
        return list
    
    def toBytes(self):
        return Matrix44.structFormat.pack(self.x.toBytes(), self.y.toBytes(), self.z.toBytes(), self.w.toBytes())
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(Matrix44.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = Matrix44.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += Matrix44.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return Matrix44.countOneOrMore(object) * Matrix44.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"y": {}, "x": {}, "z": {}, "w": {}}
    
    def getNamedBit(self, field, bitName):
        mask = Matrix44.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = Matrix44.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return Matrix44.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"x":FieldTypeInfo("VEC4V0",VEC4V0, False), "y":FieldTypeInfo("VEC4V0",VEC4V0, False), "z":FieldTypeInfo("VEC4V0",VEC4V0, False), "w":FieldTypeInfo("VEC4V0",VEC4V0, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return Matrix44.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != Matrix44:
            raise Exception("%s is not of type %s but %s" % (id, "Matrix44", type(instance)))
        fieldId = id + ".x"

        VEC4V0.validateInstance(instance.x, fieldId)
        fieldId = id + ".y"

        VEC4V0.validateInstance(instance.y, fieldId)
        fieldId = id + ".z"

        VEC4V0.validateInstance(instance.z, fieldId)
        fieldId = id + ".w"

        VEC4V0.validateInstance(instance.w, fieldId)


class Vector4As4uint8:
    """A vector out of 4 bytes which must be converted with the formula (((i / 255.0) * 2) -1) to get the actual float value"""
    tagName = "Vector4As4uint8"
    size = 4
    structFormat = struct.Struct("<BBBB")
    fields = ["x", "y", "z", "w"]

    def __setattr__(self, name, value):
        if name in ["x", "y", "z", "w"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["x", "y", "z", "w"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        pass #nothing to do
    
    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        pass #nothing to do

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert Vector4As4uint8.size == Vector4As4uint8.structFormat.size
            rawBytes = readable.read(Vector4As4uint8.size)
        if rawBytes != None:
            l = Vector4As4uint8.structFormat.unpack(rawBytes)
            self.x = l[0]
            self.y = l[1]
            self.z = l[2]
            self.w = l[3]
        if (readable == None) and (rawBytes == None):
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + Vector4As4uint8.size
        for i in range(count):
            list.append(Vector4As4uint8(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += Vector4As4uint8.size
        return list
    
    def toBytes(self):
        return Vector4As4uint8.structFormat.pack(self.x, self.y, self.z, self.w)
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(Vector4As4uint8.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = Vector4As4uint8.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += Vector4As4uint8.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return Vector4As4uint8.countOneOrMore(object) * Vector4As4uint8.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"y": {}, "x": {}, "z": {}, "w": {}}
    
    def getNamedBit(self, field, bitName):
        mask = Vector4As4uint8.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = Vector4As4uint8.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return Vector4As4uint8.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"x":FieldTypeInfo("uint8",None, False), "y":FieldTypeInfo("uint8",None, False), "z":FieldTypeInfo("uint8",None, False), "w":FieldTypeInfo("uint8",None, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return Vector4As4uint8.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != Vector4As4uint8:
            raise Exception("%s is not of type %s but %s" % (id, "Vector4As4uint8", type(instance)))
        fieldId = id + ".x"

        if (type(instance.x) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".y"

        if (type(instance.y) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".z"

        if (type(instance.z) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".w"

        if (type(instance.w) != int):
            raise Exception("%s is not an int" % (fieldId))


class Vector2As2int16:
    """A vector out of int16 values which must be converted with the formula (i / 2048.0) to get the actual float value"""
    tagName = "Vector2As2int16"
    size = 4
    structFormat = struct.Struct("<hh")
    fields = ["x", "y"]

    def __setattr__(self, name, value):
        if name in ["x", "y"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["x", "y"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        pass #nothing to do
    
    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        pass #nothing to do

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert Vector2As2int16.size == Vector2As2int16.structFormat.size
            rawBytes = readable.read(Vector2As2int16.size)
        if rawBytes != None:
            l = Vector2As2int16.structFormat.unpack(rawBytes)
            self.x = l[0]
            self.y = l[1]
        if (readable == None) and (rawBytes == None):
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + Vector2As2int16.size
        for i in range(count):
            list.append(Vector2As2int16(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += Vector2As2int16.size
        return list
    
    def toBytes(self):
        return Vector2As2int16.structFormat.pack(self.x, self.y)
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(Vector2As2int16.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = Vector2As2int16.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += Vector2As2int16.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return Vector2As2int16.countOneOrMore(object) * Vector2As2int16.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"y": {}, "x": {}}
    
    def getNamedBit(self, field, bitName):
        mask = Vector2As2int16.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = Vector2As2int16.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return Vector2As2int16.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"x":FieldTypeInfo("int16",None, False), "y":FieldTypeInfo("int16",None, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return Vector2As2int16.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != Vector2As2int16:
            raise Exception("%s is not of type %s but %s" % (id, "Vector2As2int16", type(instance)))
        fieldId = id + ".x"

        if (type(instance.x) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".y"

        if (type(instance.y) != int):
            raise Exception("%s is not an int" % (fieldId))


class COLV0:
    """Defines a color with alpha using 1 byte for each color component"""
    fullName = "COLV0"
    tagName = "COL"
    tagVersion = 0
    size = 4
    structFormat = struct.Struct("<BBBB")
    fields = ["blue", "green", "red", "alpha"]

    def __setattr__(self, name, value):
        if name in ["blue", "green", "red", "alpha"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["blue", "green", "red", "alpha"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        pass #nothing to do
    
    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        pass #nothing to do

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert COLV0.size == COLV0.structFormat.size
            rawBytes = readable.read(COLV0.size)
        if rawBytes != None:
            l = COLV0.structFormat.unpack(rawBytes)
            self.blue = l[0]
            self.green = l[1]
            self.red = l[2]
            self.alpha = l[3]
        if (readable == None) and (rawBytes == None):
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + COLV0.size
        for i in range(count):
            list.append(COLV0(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += COLV0.size
        return list
    
    def toBytes(self):
        return COLV0.structFormat.pack(self.blue, self.green, self.red, self.alpha)
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(COLV0.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = COLV0.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += COLV0.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return COLV0.countOneOrMore(object) * COLV0.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"blue": {}, "alpha": {}, "green": {}, "red": {}}
    
    def getNamedBit(self, field, bitName):
        mask = COLV0.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = COLV0.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return COLV0.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"blue":FieldTypeInfo("uint8",None, False), "green":FieldTypeInfo("uint8",None, False), "red":FieldTypeInfo("uint8",None, False), "alpha":FieldTypeInfo("uint8",None, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return COLV0.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != COLV0:
            raise Exception("%s is not of type %s but %s" % (id, "COLV0", type(instance)))
        fieldId = id + ".blue"

        if (type(instance.blue) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".green"

        if (type(instance.green) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".red"

        if (type(instance.red) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".alpha"

        if (type(instance.alpha) != int):
            raise Exception("%s is not an int" % (fieldId))


class BNDSV0:
    """
                Describes the rough shape of an object.
                Center of bounding sphere =  (extend0 + extend1)/2
            """
    fullName = "BNDSV0"
    tagName = "BNDS"
    tagVersion = 0
    size = 28
    structFormat = struct.Struct("<12s12sf")
    fields = ["min", "max", "radius"]

    def __setattr__(self, name, value):
        if name in ["min", "max", "radius"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["min", "max", "radius"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        pass #nothing to do
    
    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        pass #nothing to do

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert BNDSV0.size == BNDSV0.structFormat.size
            rawBytes = readable.read(BNDSV0.size)
        if rawBytes != None:
            l = BNDSV0.structFormat.unpack(rawBytes)
            self.min = VEC3V0(rawBytes=l[0])
            self.max = VEC3V0(rawBytes=l[1])
            self.radius = l[2]
        if (readable == None) and (rawBytes == None):
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + BNDSV0.size
        for i in range(count):
            list.append(BNDSV0(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += BNDSV0.size
        return list
    
    def toBytes(self):
        return BNDSV0.structFormat.pack(self.min.toBytes(), self.max.toBytes(), self.radius)
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(BNDSV0.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = BNDSV0.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += BNDSV0.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return BNDSV0.countOneOrMore(object) * BNDSV0.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"max": {}, "radius": {}, "min": {}}
    
    def getNamedBit(self, field, bitName):
        mask = BNDSV0.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = BNDSV0.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return BNDSV0.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"min":FieldTypeInfo("VEC3V0",VEC3V0, False), "max":FieldTypeInfo("VEC3V0",VEC3V0, False), "radius":FieldTypeInfo("float",None, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return BNDSV0.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != BNDSV0:
            raise Exception("%s is not of type %s but %s" % (id, "BNDSV0", type(instance)))
        fieldId = id + ".min"

        VEC3V0.validateInstance(instance.min, fieldId)
        fieldId = id + ".max"

        VEC3V0.validateInstance(instance.max, fieldId)
        fieldId = id + ".radius"

        if (type(instance.radius) != float):
            raise Exception("%s is not a float" % (fieldId))


class AnimationReferenceHeader:
    """
                The header of a reference to an animation entry
                flags seems to be 0 for int animations and 1 for float animations. flags is also 0 if the animation is missing
                animflags seems to be 6 if the animation reference is valid and 0 otherwise 
                animId seem to be random but unique numbers
            """
    tagName = "AnimationReferenceHeader"
    size = 8
    structFormat = struct.Struct("<HHI")
    fields = ["flags", "animFlags", "animId"]

    def __setattr__(self, name, value):
        if name in ["flags", "animFlags", "animId"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["flags", "animFlags", "animId"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        pass #nothing to do
    
    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        pass #nothing to do

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert AnimationReferenceHeader.size == AnimationReferenceHeader.structFormat.size
            rawBytes = readable.read(AnimationReferenceHeader.size)
        if rawBytes != None:
            l = AnimationReferenceHeader.structFormat.unpack(rawBytes)
            self.flags = l[0]
            self.animFlags = l[1]
            self.animId = l[2]
        if (readable == None) and (rawBytes == None):
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + AnimationReferenceHeader.size
        for i in range(count):
            list.append(AnimationReferenceHeader(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += AnimationReferenceHeader.size
        return list
    
    def toBytes(self):
        return AnimationReferenceHeader.structFormat.pack(self.flags, self.animFlags, self.animId)
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(AnimationReferenceHeader.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = AnimationReferenceHeader.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += AnimationReferenceHeader.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return AnimationReferenceHeader.countOneOrMore(object) * AnimationReferenceHeader.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"flags": {}, "animFlags": {}, "animId": {}}
    
    def getNamedBit(self, field, bitName):
        mask = AnimationReferenceHeader.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = AnimationReferenceHeader.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return AnimationReferenceHeader.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"flags":FieldTypeInfo("uint16",None, False), "animFlags":FieldTypeInfo("uint16",None, False), "animId":FieldTypeInfo("uint32",None, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return AnimationReferenceHeader.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != AnimationReferenceHeader:
            raise Exception("%s is not of type %s but %s" % (id, "AnimationReferenceHeader", type(instance)))
        fieldId = id + ".flags"

        if (type(instance.flags) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".animFlags"

        if (type(instance.animFlags) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".animId"

        if (type(instance.animId) != int):
            raise Exception("%s is not an int" % (fieldId))


class Vector3AnimationReference:
    """Animateable vector with 3 components"""
    tagName = "Vector3AnimationReference"
    size = 36
    structFormat = struct.Struct("<8s12s12sI")
    fields = ["header", "initValue", "nullValue", "unknown"]

    def __setattr__(self, name, value):
        if name in ["header", "initValue", "nullValue", "unknown"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["header", "initValue", "nullValue", "unknown"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        pass #nothing to do
    
    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        pass #nothing to do

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert Vector3AnimationReference.size == Vector3AnimationReference.structFormat.size
            rawBytes = readable.read(Vector3AnimationReference.size)
        if rawBytes != None:
            l = Vector3AnimationReference.structFormat.unpack(rawBytes)
            self.header = AnimationReferenceHeader(rawBytes=l[0])
            self.initValue = VEC3V0(rawBytes=l[1])
            self.nullValue = VEC3V0(rawBytes=l[2])
            self.unknown = l[3]
            if self.unknown != int(0):
             raise Exception("Vector3AnimationReference.unknown has value %s instead of the expected value int(0)" % self.unknown)
        if (readable == None) and (rawBytes == None):
            self.unknown = int(0)
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + Vector3AnimationReference.size
        for i in range(count):
            list.append(Vector3AnimationReference(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += Vector3AnimationReference.size
        return list
    
    def toBytes(self):
        return Vector3AnimationReference.structFormat.pack(self.header.toBytes(), self.initValue.toBytes(), self.nullValue.toBytes(), self.unknown)
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(Vector3AnimationReference.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = Vector3AnimationReference.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += Vector3AnimationReference.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return Vector3AnimationReference.countOneOrMore(object) * Vector3AnimationReference.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"initValue": {}, "header": {}, "unknown": {}, "nullValue": {}}
    
    def getNamedBit(self, field, bitName):
        mask = Vector3AnimationReference.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = Vector3AnimationReference.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return Vector3AnimationReference.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"header":FieldTypeInfo("AnimationReferenceHeader",AnimationReferenceHeader, False), "initValue":FieldTypeInfo("VEC3V0",VEC3V0, False), "nullValue":FieldTypeInfo("VEC3V0",VEC3V0, False), "unknown":FieldTypeInfo("uint32",None, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return Vector3AnimationReference.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != Vector3AnimationReference:
            raise Exception("%s is not of type %s but %s" % (id, "Vector3AnimationReference", type(instance)))
        fieldId = id + ".header"

        AnimationReferenceHeader.validateInstance(instance.header, fieldId)
        fieldId = id + ".initValue"

        VEC3V0.validateInstance(instance.initValue, fieldId)
        fieldId = id + ".nullValue"

        VEC3V0.validateInstance(instance.nullValue, fieldId)
        fieldId = id + ".unknown"

        if (type(instance.unknown) != int):
            raise Exception("%s is not an int" % (fieldId))


class Vector2AnimationReference:
    """Animatable vector with 2 components"""
    tagName = "Vector2AnimationReference"
    size = 28
    structFormat = struct.Struct("<8s8s8sI")
    fields = ["header", "initValue", "nullValue", "unknown"]

    def __setattr__(self, name, value):
        if name in ["header", "initValue", "nullValue", "unknown"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["header", "initValue", "nullValue", "unknown"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        pass #nothing to do
    
    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        pass #nothing to do

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert Vector2AnimationReference.size == Vector2AnimationReference.structFormat.size
            rawBytes = readable.read(Vector2AnimationReference.size)
        if rawBytes != None:
            l = Vector2AnimationReference.structFormat.unpack(rawBytes)
            self.header = AnimationReferenceHeader(rawBytes=l[0])
            self.initValue = VEC2V0(rawBytes=l[1])
            self.nullValue = VEC2V0(rawBytes=l[2])
            self.unknown = l[3]
        if (readable == None) and (rawBytes == None):
            self.unknown = 0
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + Vector2AnimationReference.size
        for i in range(count):
            list.append(Vector2AnimationReference(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += Vector2AnimationReference.size
        return list
    
    def toBytes(self):
        return Vector2AnimationReference.structFormat.pack(self.header.toBytes(), self.initValue.toBytes(), self.nullValue.toBytes(), self.unknown)
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(Vector2AnimationReference.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = Vector2AnimationReference.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += Vector2AnimationReference.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return Vector2AnimationReference.countOneOrMore(object) * Vector2AnimationReference.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"initValue": {}, "header": {}, "unknown": {}, "nullValue": {}}
    
    def getNamedBit(self, field, bitName):
        mask = Vector2AnimationReference.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = Vector2AnimationReference.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return Vector2AnimationReference.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"header":FieldTypeInfo("AnimationReferenceHeader",AnimationReferenceHeader, False), "initValue":FieldTypeInfo("VEC2V0",VEC2V0, False), "nullValue":FieldTypeInfo("VEC2V0",VEC2V0, False), "unknown":FieldTypeInfo("uint32",None, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return Vector2AnimationReference.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != Vector2AnimationReference:
            raise Exception("%s is not of type %s but %s" % (id, "Vector2AnimationReference", type(instance)))
        fieldId = id + ".header"

        AnimationReferenceHeader.validateInstance(instance.header, fieldId)
        fieldId = id + ".initValue"

        VEC2V0.validateInstance(instance.initValue, fieldId)
        fieldId = id + ".nullValue"

        VEC2V0.validateInstance(instance.nullValue, fieldId)
        fieldId = id + ".unknown"

        if (type(instance.unknown) != int):
            raise Exception("%s is not an int" % (fieldId))


class QuaternionAnimationReference:
    """Animatable vector4"""
    tagName = "QuaternionAnimationReference"
    size = 44
    structFormat = struct.Struct("<8s16s16sI")
    fields = ["header", "initValue", "nullValue", "unknown"]

    def __setattr__(self, name, value):
        if name in ["header", "initValue", "nullValue", "unknown"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["header", "initValue", "nullValue", "unknown"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        pass #nothing to do
    
    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        pass #nothing to do

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert QuaternionAnimationReference.size == QuaternionAnimationReference.structFormat.size
            rawBytes = readable.read(QuaternionAnimationReference.size)
        if rawBytes != None:
            l = QuaternionAnimationReference.structFormat.unpack(rawBytes)
            self.header = AnimationReferenceHeader(rawBytes=l[0])
            self.initValue = QUATV0(rawBytes=l[1])
            self.nullValue = QUATV0(rawBytes=l[2])
            self.unknown = l[3]
            if self.unknown != int(0):
             raise Exception("QuaternionAnimationReference.unknown has value %s instead of the expected value int(0)" % self.unknown)
        if (readable == None) and (rawBytes == None):
            self.unknown = int(0)
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + QuaternionAnimationReference.size
        for i in range(count):
            list.append(QuaternionAnimationReference(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += QuaternionAnimationReference.size
        return list
    
    def toBytes(self):
        return QuaternionAnimationReference.structFormat.pack(self.header.toBytes(), self.initValue.toBytes(), self.nullValue.toBytes(), self.unknown)
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(QuaternionAnimationReference.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = QuaternionAnimationReference.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += QuaternionAnimationReference.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return QuaternionAnimationReference.countOneOrMore(object) * QuaternionAnimationReference.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"initValue": {}, "header": {}, "unknown": {}, "nullValue": {}}
    
    def getNamedBit(self, field, bitName):
        mask = QuaternionAnimationReference.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = QuaternionAnimationReference.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return QuaternionAnimationReference.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"header":FieldTypeInfo("AnimationReferenceHeader",AnimationReferenceHeader, False), "initValue":FieldTypeInfo("QUATV0",QUATV0, False), "nullValue":FieldTypeInfo("QUATV0",QUATV0, False), "unknown":FieldTypeInfo("uint32",None, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return QuaternionAnimationReference.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != QuaternionAnimationReference:
            raise Exception("%s is not of type %s but %s" % (id, "QuaternionAnimationReference", type(instance)))
        fieldId = id + ".header"

        AnimationReferenceHeader.validateInstance(instance.header, fieldId)
        fieldId = id + ".initValue"

        QUATV0.validateInstance(instance.initValue, fieldId)
        fieldId = id + ".nullValue"

        QUATV0.validateInstance(instance.nullValue, fieldId)
        fieldId = id + ".unknown"

        if (type(instance.unknown) != int):
            raise Exception("%s is not an int" % (fieldId))


class UInt32AnimationReference:
    """Animatable  uint32"""
    tagName = "UInt32AnimationReference"
    size = 20
    structFormat = struct.Struct("<8sIII")
    fields = ["header", "initValue", "nullValue", "unknown"]

    def __setattr__(self, name, value):
        if name in ["header", "initValue", "nullValue", "unknown"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["header", "initValue", "nullValue", "unknown"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        pass #nothing to do
    
    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        pass #nothing to do

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert UInt32AnimationReference.size == UInt32AnimationReference.structFormat.size
            rawBytes = readable.read(UInt32AnimationReference.size)
        if rawBytes != None:
            l = UInt32AnimationReference.structFormat.unpack(rawBytes)
            self.header = AnimationReferenceHeader(rawBytes=l[0])
            self.initValue = l[1]
            self.nullValue = l[2]
            self.unknown = l[3]
            if self.unknown != int(0):
             raise Exception("UInt32AnimationReference.unknown has value %s instead of the expected value int(0)" % self.unknown)
        if (readable == None) and (rawBytes == None):
            self.unknown = int(0)
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + UInt32AnimationReference.size
        for i in range(count):
            list.append(UInt32AnimationReference(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += UInt32AnimationReference.size
        return list
    
    def toBytes(self):
        return UInt32AnimationReference.structFormat.pack(self.header.toBytes(), self.initValue, self.nullValue, self.unknown)
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(UInt32AnimationReference.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = UInt32AnimationReference.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += UInt32AnimationReference.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return UInt32AnimationReference.countOneOrMore(object) * UInt32AnimationReference.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"initValue": {}, "header": {}, "unknown": {}, "nullValue": {}}
    
    def getNamedBit(self, field, bitName):
        mask = UInt32AnimationReference.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = UInt32AnimationReference.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return UInt32AnimationReference.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"header":FieldTypeInfo("AnimationReferenceHeader",AnimationReferenceHeader, False), "initValue":FieldTypeInfo("uint32",None, False), "nullValue":FieldTypeInfo("uint32",None, False), "unknown":FieldTypeInfo("uint32",None, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return UInt32AnimationReference.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != UInt32AnimationReference:
            raise Exception("%s is not of type %s but %s" % (id, "UInt32AnimationReference", type(instance)))
        fieldId = id + ".header"

        AnimationReferenceHeader.validateInstance(instance.header, fieldId)
        fieldId = id + ".initValue"

        if (type(instance.initValue) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".nullValue"

        if (type(instance.nullValue) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".unknown"

        if (type(instance.unknown) != int):
            raise Exception("%s is not an int" % (fieldId))


class UInt16AnimationReference:
    """Animatable uint16"""
    tagName = "UInt16AnimationReference"
    size = 16
    structFormat = struct.Struct("<8sHHI")
    fields = ["header", "initValue", "nullValue", "unknown"]

    def __setattr__(self, name, value):
        if name in ["header", "initValue", "nullValue", "unknown"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["header", "initValue", "nullValue", "unknown"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        pass #nothing to do
    
    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        pass #nothing to do

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert UInt16AnimationReference.size == UInt16AnimationReference.structFormat.size
            rawBytes = readable.read(UInt16AnimationReference.size)
        if rawBytes != None:
            l = UInt16AnimationReference.structFormat.unpack(rawBytes)
            self.header = AnimationReferenceHeader(rawBytes=l[0])
            self.initValue = l[1]
            self.nullValue = l[2]
            self.unknown = l[3]
            if self.unknown != int(0):
             raise Exception("UInt16AnimationReference.unknown has value %s instead of the expected value int(0)" % self.unknown)
        if (readable == None) and (rawBytes == None):
            self.unknown = int(0)
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + UInt16AnimationReference.size
        for i in range(count):
            list.append(UInt16AnimationReference(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += UInt16AnimationReference.size
        return list
    
    def toBytes(self):
        return UInt16AnimationReference.structFormat.pack(self.header.toBytes(), self.initValue, self.nullValue, self.unknown)
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(UInt16AnimationReference.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = UInt16AnimationReference.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += UInt16AnimationReference.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return UInt16AnimationReference.countOneOrMore(object) * UInt16AnimationReference.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"initValue": {}, "header": {}, "unknown": {}, "nullValue": {}}
    
    def getNamedBit(self, field, bitName):
        mask = UInt16AnimationReference.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = UInt16AnimationReference.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return UInt16AnimationReference.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"header":FieldTypeInfo("AnimationReferenceHeader",AnimationReferenceHeader, False), "initValue":FieldTypeInfo("uint16",None, False), "nullValue":FieldTypeInfo("uint16",None, False), "unknown":FieldTypeInfo("uint32",None, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return UInt16AnimationReference.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != UInt16AnimationReference:
            raise Exception("%s is not of type %s but %s" % (id, "UInt16AnimationReference", type(instance)))
        fieldId = id + ".header"

        AnimationReferenceHeader.validateInstance(instance.header, fieldId)
        fieldId = id + ".initValue"

        if (type(instance.initValue) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".nullValue"

        if (type(instance.nullValue) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".unknown"

        if (type(instance.unknown) != int):
            raise Exception("%s is not an int" % (fieldId))


class Int16AnimationReference:
    """Animatable int16"""
    tagName = "Int16AnimationReference"
    size = 16
    structFormat = struct.Struct("<8shhI")
    fields = ["header", "initValue", "nullValue", "unknown"]

    def __setattr__(self, name, value):
        if name in ["header", "initValue", "nullValue", "unknown"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["header", "initValue", "nullValue", "unknown"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        pass #nothing to do
    
    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        pass #nothing to do

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert Int16AnimationReference.size == Int16AnimationReference.structFormat.size
            rawBytes = readable.read(Int16AnimationReference.size)
        if rawBytes != None:
            l = Int16AnimationReference.structFormat.unpack(rawBytes)
            self.header = AnimationReferenceHeader(rawBytes=l[0])
            self.initValue = l[1]
            self.nullValue = l[2]
            self.unknown = l[3]
            if self.unknown != int(0):
             raise Exception("Int16AnimationReference.unknown has value %s instead of the expected value int(0)" % self.unknown)
        if (readable == None) and (rawBytes == None):
            self.unknown = int(0)
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + Int16AnimationReference.size
        for i in range(count):
            list.append(Int16AnimationReference(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += Int16AnimationReference.size
        return list
    
    def toBytes(self):
        return Int16AnimationReference.structFormat.pack(self.header.toBytes(), self.initValue, self.nullValue, self.unknown)
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(Int16AnimationReference.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = Int16AnimationReference.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += Int16AnimationReference.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return Int16AnimationReference.countOneOrMore(object) * Int16AnimationReference.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"initValue": {}, "header": {}, "unknown": {}, "nullValue": {}}
    
    def getNamedBit(self, field, bitName):
        mask = Int16AnimationReference.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = Int16AnimationReference.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return Int16AnimationReference.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"header":FieldTypeInfo("AnimationReferenceHeader",AnimationReferenceHeader, False), "initValue":FieldTypeInfo("int16",None, False), "nullValue":FieldTypeInfo("int16",None, False), "unknown":FieldTypeInfo("uint32",None, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return Int16AnimationReference.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != Int16AnimationReference:
            raise Exception("%s is not of type %s but %s" % (id, "Int16AnimationReference", type(instance)))
        fieldId = id + ".header"

        AnimationReferenceHeader.validateInstance(instance.header, fieldId)
        fieldId = id + ".initValue"

        if (type(instance.initValue) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".nullValue"

        if (type(instance.nullValue) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".unknown"

        if (type(instance.unknown) != int):
            raise Exception("%s is not an int" % (fieldId))


class FloatAnimationReference:
    """Animatable float"""
    tagName = "FloatAnimationReference"
    size = 20
    structFormat = struct.Struct("<8sffI")
    fields = ["header", "initValue", "nullValue", "unknown"]

    def __setattr__(self, name, value):
        if name in ["header", "initValue", "nullValue", "unknown"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["header", "initValue", "nullValue", "unknown"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        pass #nothing to do
    
    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        pass #nothing to do

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert FloatAnimationReference.size == FloatAnimationReference.structFormat.size
            rawBytes = readable.read(FloatAnimationReference.size)
        if rawBytes != None:
            l = FloatAnimationReference.structFormat.unpack(rawBytes)
            self.header = AnimationReferenceHeader(rawBytes=l[0])
            self.initValue = l[1]
            self.nullValue = l[2]
            self.unknown = l[3]
            if self.unknown != int(0):
             raise Exception("FloatAnimationReference.unknown has value %s instead of the expected value int(0)" % self.unknown)
        if (readable == None) and (rawBytes == None):
            self.unknown = int(0)
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + FloatAnimationReference.size
        for i in range(count):
            list.append(FloatAnimationReference(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += FloatAnimationReference.size
        return list
    
    def toBytes(self):
        return FloatAnimationReference.structFormat.pack(self.header.toBytes(), self.initValue, self.nullValue, self.unknown)
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(FloatAnimationReference.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = FloatAnimationReference.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += FloatAnimationReference.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return FloatAnimationReference.countOneOrMore(object) * FloatAnimationReference.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"initValue": {}, "header": {}, "unknown": {}, "nullValue": {}}
    
    def getNamedBit(self, field, bitName):
        mask = FloatAnimationReference.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = FloatAnimationReference.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return FloatAnimationReference.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"header":FieldTypeInfo("AnimationReferenceHeader",AnimationReferenceHeader, False), "initValue":FieldTypeInfo("float",None, False), "nullValue":FieldTypeInfo("float",None, False), "unknown":FieldTypeInfo("uint32",None, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return FloatAnimationReference.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != FloatAnimationReference:
            raise Exception("%s is not of type %s but %s" % (id, "FloatAnimationReference", type(instance)))
        fieldId = id + ".header"

        AnimationReferenceHeader.validateInstance(instance.header, fieldId)
        fieldId = id + ".initValue"

        if (type(instance.initValue) != float):
            raise Exception("%s is not a float" % (fieldId))
        fieldId = id + ".nullValue"

        if (type(instance.nullValue) != float):
            raise Exception("%s is not a float" % (fieldId))
        fieldId = id + ".unknown"

        if (type(instance.unknown) != int):
            raise Exception("%s is not an int" % (fieldId))


class ColorAnimationReference:
    """Animatable color"""
    tagName = "ColorAnimationReference"
    size = 20
    structFormat = struct.Struct("<8s4s4sI")
    fields = ["header", "initValue", "nullValue", "unknown"]

    def __setattr__(self, name, value):
        if name in ["header", "initValue", "nullValue", "unknown"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["header", "initValue", "nullValue", "unknown"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        pass #nothing to do
    
    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        pass #nothing to do

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert ColorAnimationReference.size == ColorAnimationReference.structFormat.size
            rawBytes = readable.read(ColorAnimationReference.size)
        if rawBytes != None:
            l = ColorAnimationReference.structFormat.unpack(rawBytes)
            self.header = AnimationReferenceHeader(rawBytes=l[0])
            self.initValue = COLV0(rawBytes=l[1])
            self.nullValue = COLV0(rawBytes=l[2])
            self.unknown = l[3]
            if self.unknown != int(0):
             raise Exception("ColorAnimationReference.unknown has value %s instead of the expected value int(0)" % self.unknown)
        if (readable == None) and (rawBytes == None):
            self.unknown = int(0)
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + ColorAnimationReference.size
        for i in range(count):
            list.append(ColorAnimationReference(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += ColorAnimationReference.size
        return list
    
    def toBytes(self):
        return ColorAnimationReference.structFormat.pack(self.header.toBytes(), self.initValue.toBytes(), self.nullValue.toBytes(), self.unknown)
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(ColorAnimationReference.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = ColorAnimationReference.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += ColorAnimationReference.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return ColorAnimationReference.countOneOrMore(object) * ColorAnimationReference.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"initValue": {}, "header": {}, "unknown": {}, "nullValue": {}}
    
    def getNamedBit(self, field, bitName):
        mask = ColorAnimationReference.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = ColorAnimationReference.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return ColorAnimationReference.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"header":FieldTypeInfo("AnimationReferenceHeader",AnimationReferenceHeader, False), "initValue":FieldTypeInfo("COLV0",COLV0, False), "nullValue":FieldTypeInfo("COLV0",COLV0, False), "unknown":FieldTypeInfo("uint32",None, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return ColorAnimationReference.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != ColorAnimationReference:
            raise Exception("%s is not of type %s but %s" % (id, "ColorAnimationReference", type(instance)))
        fieldId = id + ".header"

        AnimationReferenceHeader.validateInstance(instance.header, fieldId)
        fieldId = id + ".initValue"

        COLV0.validateInstance(instance.initValue, fieldId)
        fieldId = id + ".nullValue"

        COLV0.validateInstance(instance.nullValue, fieldId)
        fieldId = id + ".unknown"

        if (type(instance.unknown) != int):
            raise Exception("%s is not an int" % (fieldId))


class BNDSV0AnimationReference:
    """Animatable boundings"""
    tagName = "BNDSV0AnimationReference"
    size = 68
    structFormat = struct.Struct("<8s28s28sI")
    fields = ["header", "initValue", "nullValue", "unknown"]

    def __setattr__(self, name, value):
        if name in ["header", "initValue", "nullValue", "unknown"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["header", "initValue", "nullValue", "unknown"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        pass #nothing to do
    
    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        pass #nothing to do

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert BNDSV0AnimationReference.size == BNDSV0AnimationReference.structFormat.size
            rawBytes = readable.read(BNDSV0AnimationReference.size)
        if rawBytes != None:
            l = BNDSV0AnimationReference.structFormat.unpack(rawBytes)
            self.header = AnimationReferenceHeader(rawBytes=l[0])
            self.initValue = BNDSV0(rawBytes=l[1])
            self.nullValue = BNDSV0(rawBytes=l[2])
            self.unknown = l[3]
            if self.unknown != int(0):
             raise Exception("BNDSV0AnimationReference.unknown has value %s instead of the expected value int(0)" % self.unknown)
        if (readable == None) and (rawBytes == None):
            self.unknown = int(0)
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + BNDSV0AnimationReference.size
        for i in range(count):
            list.append(BNDSV0AnimationReference(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += BNDSV0AnimationReference.size
        return list
    
    def toBytes(self):
        return BNDSV0AnimationReference.structFormat.pack(self.header.toBytes(), self.initValue.toBytes(), self.nullValue.toBytes(), self.unknown)
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(BNDSV0AnimationReference.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = BNDSV0AnimationReference.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += BNDSV0AnimationReference.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return BNDSV0AnimationReference.countOneOrMore(object) * BNDSV0AnimationReference.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"initValue": {}, "header": {}, "unknown": {}, "nullValue": {}}
    
    def getNamedBit(self, field, bitName):
        mask = BNDSV0AnimationReference.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = BNDSV0AnimationReference.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return BNDSV0AnimationReference.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"header":FieldTypeInfo("AnimationReferenceHeader",AnimationReferenceHeader, False), "initValue":FieldTypeInfo("BNDSV0",BNDSV0, False), "nullValue":FieldTypeInfo("BNDSV0",BNDSV0, False), "unknown":FieldTypeInfo("uint32",None, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return BNDSV0AnimationReference.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != BNDSV0AnimationReference:
            raise Exception("%s is not of type %s but %s" % (id, "BNDSV0AnimationReference", type(instance)))
        fieldId = id + ".header"

        AnimationReferenceHeader.validateInstance(instance.header, fieldId)
        fieldId = id + ".initValue"

        BNDSV0.validateInstance(instance.initValue, fieldId)
        fieldId = id + ".nullValue"

        BNDSV0.validateInstance(instance.nullValue, fieldId)
        fieldId = id + ".unknown"

        if (type(instance.unknown) != int):
            raise Exception("%s is not an int" % (fieldId))


class REALV0:
    """A float"""
    fullName = "REALV0"
    tagName = "REAL"
    tagVersion = 0
    size = 4
    structFormat = struct.Struct("<f")
    fields = ["value"]

    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        pass #nothing to do
    
    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        pass #nothing to do

    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        for offset in range(0, count*REALV0.size, REALV0.size):
            bytesOfOneEntry = rawBytes[offset:(offset+REALV0.size)]
            intValue = REALV0.structFormat.unpack(bytesOfOneEntry)[0]
            list.append(intValue)
        return list
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(REALV0.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = REALV0.size
        for object in list:
            rawBytes[offset:nextOffset] = REALV0.structFormat.pack(object)
            offset = nextOffset
            nextOffset += REALV0.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return REALV0.countOneOrMore(object) * REALV0.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"value": {}}
    
    def getNamedBit(self, field, bitName):
        mask = REALV0.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = REALV0.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return REALV0.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"value":FieldTypeInfo("float",None, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return REALV0.fieldToTypeInfoMap[fieldName]
    
class CHARV0:
    """An one byte character. An array always terminates with 0."""
    fullName = "CHARV0"
    tagName = "CHAR"
    tagVersion = 0
    size = 1
    structFormat = struct.Struct("<B")
    fields = ["value"]

    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        pass #nothing to do
    
    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        pass #nothing to do

    @staticmethod
    def createInstances(rawBytes, count):
        return rawBytes[:count-1].decode("ASCII")
    
    def rawBytesForOneOrMore(oneOrMore):
        return oneOrMore.encode("ASCII") + b"\x00"
    
    @staticmethod
    def countOneOrMore(object):
        if object == None:
            return 0
        return len(object)+1 # +1 terminating null character
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return CHARV0.countOneOrMore(object) * CHARV0.size
    
    @staticmethod
    def createEmptyArray():
        return None # even no terminating character
    
    fieldToBitMaskMapMap = {"value": {}}
    
    def getNamedBit(self, field, bitName):
        mask = CHARV0.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = CHARV0.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return CHARV0.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"value":FieldTypeInfo("uint8",None, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return CHARV0.fieldToTypeInfoMap[fieldName]
    
class U8__V0:
    """An unsigned integer"""
    fullName = "U8__V0"
    tagName = "U8__"
    tagVersion = 0
    size = 1
    structFormat = struct.Struct("<B")
    fields = ["value"]

    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        pass #nothing to do
    
    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        pass #nothing to do

    @staticmethod
    def createInstances(rawBytes, count):
        return bytearray(rawBytes)
    
    def rawBytesForOneOrMore(oneOrMore):
        return oneOrMore
    
    @staticmethod
    def countOneOrMore(object):
        return len(object)
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return U8__V0.countOneOrMore(object) * U8__V0.size
    
    @staticmethod
    def createEmptyArray():
        return bytearray(0)
    
    fieldToBitMaskMapMap = {"value": {}}
    
    def getNamedBit(self, field, bitName):
        mask = U8__V0.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = U8__V0.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return U8__V0.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"value":FieldTypeInfo("uint8",None, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return U8__V0.fieldToTypeInfoMap[fieldName]
    
class I16_V0:
    """An signed integer with 16 bits"""
    fullName = "I16_V0"
    tagName = "I16_"
    tagVersion = 0
    size = 2
    structFormat = struct.Struct("<h")
    fields = ["value"]

    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        pass #nothing to do
    
    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        pass #nothing to do

    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        for offset in range(0, count*I16_V0.size, I16_V0.size):
            bytesOfOneEntry = rawBytes[offset:(offset+I16_V0.size)]
            intValue = I16_V0.structFormat.unpack(bytesOfOneEntry)[0]
            list.append(intValue)
        return list
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(I16_V0.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = I16_V0.size
        for object in list:
            rawBytes[offset:nextOffset] = I16_V0.structFormat.pack(object)
            offset = nextOffset
            nextOffset += I16_V0.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return I16_V0.countOneOrMore(object) * I16_V0.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"value": {}}
    
    def getNamedBit(self, field, bitName):
        mask = I16_V0.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = I16_V0.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return I16_V0.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"value":FieldTypeInfo("int16",None, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return I16_V0.fieldToTypeInfoMap[fieldName]
    
class U16_V0:
    """An unsigned integer with 16 bits"""
    fullName = "U16_V0"
    tagName = "U16_"
    tagVersion = 0
    size = 2
    structFormat = struct.Struct("<H")
    fields = ["value"]

    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        pass #nothing to do
    
    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        pass #nothing to do

    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        for offset in range(0, count*U16_V0.size, U16_V0.size):
            bytesOfOneEntry = rawBytes[offset:(offset+U16_V0.size)]
            intValue = U16_V0.structFormat.unpack(bytesOfOneEntry)[0]
            list.append(intValue)
        return list
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(U16_V0.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = U16_V0.size
        for object in list:
            rawBytes[offset:nextOffset] = U16_V0.structFormat.pack(object)
            offset = nextOffset
            nextOffset += U16_V0.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return U16_V0.countOneOrMore(object) * U16_V0.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"value": {}}
    
    def getNamedBit(self, field, bitName):
        mask = U16_V0.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = U16_V0.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return U16_V0.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"value":FieldTypeInfo("uint16",None, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return U16_V0.fieldToTypeInfoMap[fieldName]
    
class I32_V0:
    """An signed integer """
    fullName = "I32_V0"
    tagName = "I32_"
    tagVersion = 0
    size = 4
    structFormat = struct.Struct("<i")
    fields = ["value"]

    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        pass #nothing to do
    
    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        pass #nothing to do

    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        for offset in range(0, count*I32_V0.size, I32_V0.size):
            bytesOfOneEntry = rawBytes[offset:(offset+I32_V0.size)]
            intValue = I32_V0.structFormat.unpack(bytesOfOneEntry)[0]
            list.append(intValue)
        return list
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(I32_V0.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = I32_V0.size
        for object in list:
            rawBytes[offset:nextOffset] = I32_V0.structFormat.pack(object)
            offset = nextOffset
            nextOffset += I32_V0.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return I32_V0.countOneOrMore(object) * I32_V0.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"value": {}}
    
    def getNamedBit(self, field, bitName):
        mask = I32_V0.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = I32_V0.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return I32_V0.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"value":FieldTypeInfo("int32",None, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return I32_V0.fieldToTypeInfoMap[fieldName]
    
class U32_V0:
    """An unsigned integer"""
    fullName = "U32_V0"
    tagName = "U32_"
    tagVersion = 0
    size = 4
    structFormat = struct.Struct("<I")
    fields = ["value"]

    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        pass #nothing to do
    
    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        pass #nothing to do

    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        for offset in range(0, count*U32_V0.size, U32_V0.size):
            bytesOfOneEntry = rawBytes[offset:(offset+U32_V0.size)]
            intValue = U32_V0.structFormat.unpack(bytesOfOneEntry)[0]
            list.append(intValue)
        return list
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(U32_V0.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = U32_V0.size
        for object in list:
            rawBytes[offset:nextOffset] = U32_V0.structFormat.pack(object)
            offset = nextOffset
            nextOffset += U32_V0.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return U32_V0.countOneOrMore(object) * U32_V0.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"value": {}}
    
    def getNamedBit(self, field, bitName):
        mask = U32_V0.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = U32_V0.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return U32_V0.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"value":FieldTypeInfo("uint32",None, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return U32_V0.fieldToTypeInfoMap[fieldName]
    
class MD34IndexEntry:
    """Entry of the tag index. Position and size of the tag index gets desribed by MD34"""
    tagName = "MD34IndexEntry"
    size = 16
    structFormat = struct.Struct("<4sIII")
    fields = ["tag", "offset", "repetitions", "version"]

    def __setattr__(self, name, value):
        if name in ["tag", "offset", "repetitions", "version"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["tag", "offset", "repetitions", "version"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        pass #nothing to do
    
    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        pass #nothing to do

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert MD34IndexEntry.size == MD34IndexEntry.structFormat.size
            rawBytes = readable.read(MD34IndexEntry.size)
        if rawBytes != None:
            l = MD34IndexEntry.structFormat.unpack(rawBytes)
            self.tag = unpackTag(l[0])
            self.offset = l[1]
            self.repetitions = l[2]
            self.version = l[3]
        if (readable == None) and (rawBytes == None):
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + MD34IndexEntry.size
        for i in range(count):
            list.append(MD34IndexEntry(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += MD34IndexEntry.size
        return list
    
    def toBytes(self):
        return MD34IndexEntry.structFormat.pack(packTag(self.tag), self.offset, self.repetitions, self.version)
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(MD34IndexEntry.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = MD34IndexEntry.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += MD34IndexEntry.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return MD34IndexEntry.countOneOrMore(object) * MD34IndexEntry.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"repetitions": {}, "tag": {}, "version": {}, "offset": {}}
    
    def getNamedBit(self, field, bitName):
        mask = MD34IndexEntry.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = MD34IndexEntry.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return MD34IndexEntry.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"tag":FieldTypeInfo("tag",None, False), "offset":FieldTypeInfo("uint32",None, False), "repetitions":FieldTypeInfo("uint32",None, False), "version":FieldTypeInfo("uint32",None, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return MD34IndexEntry.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != MD34IndexEntry:
            raise Exception("%s is not of type %s but %s" % (id, "MD34IndexEntry", type(instance)))
        fieldId = id + ".tag"
        if (type(instance.tag) != str) or (len(instance.tag) != 4):
            raise Exception("%s is not a string with 4 characters" % (fieldId))
        fieldId = id + ".offset"

        if (type(instance.offset) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".repetitions"

        if (type(instance.repetitions) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".version"

        if (type(instance.version) != int):
            raise Exception("%s is not an int" % (fieldId))


class VertexFormat0x182007d:
    """Vertex with one UV coordinate"""
    tagName = "VertexFormat0x182007d"
    size = 32
    structFormat = struct.Struct("<12sBBBBBBBB4s4s4s")
    fields = ["position", "boneWeight0", "boneWeight1", "boneWeight2", "boneWeight3", "boneLookupIndex0", "boneLookupIndex1", "boneLookupIndex2", "boneLookupIndex3", "normal", "uv0", "tangent"]

    def __setattr__(self, name, value):
        if name in ["position", "boneWeight0", "boneWeight1", "boneWeight2", "boneWeight3", "boneLookupIndex0", "boneLookupIndex1", "boneLookupIndex2", "boneLookupIndex3", "normal", "uv0", "tangent"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["position", "boneWeight0", "boneWeight1", "boneWeight2", "boneWeight3", "boneLookupIndex0", "boneLookupIndex1", "boneLookupIndex2", "boneLookupIndex3", "normal", "uv0", "tangent"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        pass #nothing to do
    
    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        pass #nothing to do

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert VertexFormat0x182007d.size == VertexFormat0x182007d.structFormat.size
            rawBytes = readable.read(VertexFormat0x182007d.size)
        if rawBytes != None:
            l = VertexFormat0x182007d.structFormat.unpack(rawBytes)
            self.position = VEC3V0(rawBytes=l[0])
            self.boneWeight0 = l[1]
            self.boneWeight1 = l[2]
            self.boneWeight2 = l[3]
            self.boneWeight3 = l[4]
            self.boneLookupIndex0 = l[5]
            self.boneLookupIndex1 = l[6]
            self.boneLookupIndex2 = l[7]
            self.boneLookupIndex3 = l[8]
            self.normal = Vector4As4uint8(rawBytes=l[9])
            self.uv0 = Vector2As2int16(rawBytes=l[10])
            self.tangent = Vector4As4uint8(rawBytes=l[11])
        if (readable == None) and (rawBytes == None):
            self.boneWeight0 = 0
            self.boneWeight1 = 0
            self.boneWeight2 = 0
            self.boneWeight3 = 0
            self.boneLookupIndex0 = 0
            self.boneLookupIndex1 = 0
            self.boneLookupIndex2 = 0
            self.boneLookupIndex3 = 0
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + VertexFormat0x182007d.size
        for i in range(count):
            list.append(VertexFormat0x182007d(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += VertexFormat0x182007d.size
        return list
    
    def toBytes(self):
        return VertexFormat0x182007d.structFormat.pack(self.position.toBytes(), self.boneWeight0, self.boneWeight1, self.boneWeight2, self.boneWeight3, self.boneLookupIndex0, self.boneLookupIndex1, self.boneLookupIndex2, self.boneLookupIndex3, self.normal.toBytes(), self.uv0.toBytes(), self.tangent.toBytes())
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(VertexFormat0x182007d.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = VertexFormat0x182007d.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += VertexFormat0x182007d.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return VertexFormat0x182007d.countOneOrMore(object) * VertexFormat0x182007d.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"normal": {}, "uv0": {}, "boneWeight1": {}, "boneLookupIndex0": {}, "boneWeight0": {}, "boneWeight3": {}, "boneWeight2": {}, "tangent": {}, "boneLookupIndex2": {}, "position": {}, "boneLookupIndex3": {}, "boneLookupIndex1": {}}
    
    def getNamedBit(self, field, bitName):
        mask = VertexFormat0x182007d.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = VertexFormat0x182007d.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return VertexFormat0x182007d.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"position":FieldTypeInfo("VEC3V0",VEC3V0, False), "boneWeight0":FieldTypeInfo("uint8",None, False), "boneWeight1":FieldTypeInfo("uint8",None, False), "boneWeight2":FieldTypeInfo("uint8",None, False), "boneWeight3":FieldTypeInfo("uint8",None, False), "boneLookupIndex0":FieldTypeInfo("uint8",None, False), "boneLookupIndex1":FieldTypeInfo("uint8",None, False), "boneLookupIndex2":FieldTypeInfo("uint8",None, False), "boneLookupIndex3":FieldTypeInfo("uint8",None, False), "normal":FieldTypeInfo("Vector4As4uint8",Vector4As4uint8, False), "uv0":FieldTypeInfo("Vector2As2int16",Vector2As2int16, False), "tangent":FieldTypeInfo("Vector4As4uint8",Vector4As4uint8, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return VertexFormat0x182007d.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != VertexFormat0x182007d:
            raise Exception("%s is not of type %s but %s" % (id, "VertexFormat0x182007d", type(instance)))
        fieldId = id + ".position"

        VEC3V0.validateInstance(instance.position, fieldId)
        fieldId = id + ".boneWeight0"

        if (type(instance.boneWeight0) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".boneWeight1"

        if (type(instance.boneWeight1) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".boneWeight2"

        if (type(instance.boneWeight2) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".boneWeight3"

        if (type(instance.boneWeight3) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".boneLookupIndex0"

        if (type(instance.boneLookupIndex0) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".boneLookupIndex1"

        if (type(instance.boneLookupIndex1) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".boneLookupIndex2"

        if (type(instance.boneLookupIndex2) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".boneLookupIndex3"

        if (type(instance.boneLookupIndex3) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".normal"

        Vector4As4uint8.validateInstance(instance.normal, fieldId)
        fieldId = id + ".uv0"

        Vector2As2int16.validateInstance(instance.uv0, fieldId)
        fieldId = id + ".tangent"

        Vector4As4uint8.validateInstance(instance.tangent, fieldId)


class VertexFormat0x186007d:
    """Vertex with two UV coordinates"""
    tagName = "VertexFormat0x186007d"
    size = 36
    structFormat = struct.Struct("<12sBBBBBBBB4s4s4s4s")
    fields = ["position", "boneWeight0", "boneWeight1", "boneWeight2", "boneWeight3", "boneLookupIndex0", "boneLookupIndex1", "boneLookupIndex2", "boneLookupIndex3", "normal", "uv0", "uv1", "tangent"]

    def __setattr__(self, name, value):
        if name in ["position", "boneWeight0", "boneWeight1", "boneWeight2", "boneWeight3", "boneLookupIndex0", "boneLookupIndex1", "boneLookupIndex2", "boneLookupIndex3", "normal", "uv0", "uv1", "tangent"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["position", "boneWeight0", "boneWeight1", "boneWeight2", "boneWeight3", "boneLookupIndex0", "boneLookupIndex1", "boneLookupIndex2", "boneLookupIndex3", "normal", "uv0", "uv1", "tangent"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        pass #nothing to do
    
    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        pass #nothing to do

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert VertexFormat0x186007d.size == VertexFormat0x186007d.structFormat.size
            rawBytes = readable.read(VertexFormat0x186007d.size)
        if rawBytes != None:
            l = VertexFormat0x186007d.structFormat.unpack(rawBytes)
            self.position = VEC3V0(rawBytes=l[0])
            self.boneWeight0 = l[1]
            self.boneWeight1 = l[2]
            self.boneWeight2 = l[3]
            self.boneWeight3 = l[4]
            self.boneLookupIndex0 = l[5]
            self.boneLookupIndex1 = l[6]
            self.boneLookupIndex2 = l[7]
            self.boneLookupIndex3 = l[8]
            self.normal = Vector4As4uint8(rawBytes=l[9])
            self.uv0 = Vector2As2int16(rawBytes=l[10])
            self.uv1 = Vector2As2int16(rawBytes=l[11])
            self.tangent = Vector4As4uint8(rawBytes=l[12])
        if (readable == None) and (rawBytes == None):
            self.boneWeight0 = 0
            self.boneWeight1 = 0
            self.boneWeight2 = 0
            self.boneWeight3 = 0
            self.boneLookupIndex0 = 0
            self.boneLookupIndex1 = 0
            self.boneLookupIndex2 = 0
            self.boneLookupIndex3 = 0
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + VertexFormat0x186007d.size
        for i in range(count):
            list.append(VertexFormat0x186007d(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += VertexFormat0x186007d.size
        return list
    
    def toBytes(self):
        return VertexFormat0x186007d.structFormat.pack(self.position.toBytes(), self.boneWeight0, self.boneWeight1, self.boneWeight2, self.boneWeight3, self.boneLookupIndex0, self.boneLookupIndex1, self.boneLookupIndex2, self.boneLookupIndex3, self.normal.toBytes(), self.uv0.toBytes(), self.uv1.toBytes(), self.tangent.toBytes())
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(VertexFormat0x186007d.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = VertexFormat0x186007d.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += VertexFormat0x186007d.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return VertexFormat0x186007d.countOneOrMore(object) * VertexFormat0x186007d.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"normal": {}, "uv0": {}, "boneWeight1": {}, "boneLookupIndex0": {}, "boneWeight0": {}, "boneWeight3": {}, "boneWeight2": {}, "tangent": {}, "boneLookupIndex2": {}, "uv1": {}, "position": {}, "boneLookupIndex3": {}, "boneLookupIndex1": {}}
    
    def getNamedBit(self, field, bitName):
        mask = VertexFormat0x186007d.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = VertexFormat0x186007d.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return VertexFormat0x186007d.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"position":FieldTypeInfo("VEC3V0",VEC3V0, False), "boneWeight0":FieldTypeInfo("uint8",None, False), "boneWeight1":FieldTypeInfo("uint8",None, False), "boneWeight2":FieldTypeInfo("uint8",None, False), "boneWeight3":FieldTypeInfo("uint8",None, False), "boneLookupIndex0":FieldTypeInfo("uint8",None, False), "boneLookupIndex1":FieldTypeInfo("uint8",None, False), "boneLookupIndex2":FieldTypeInfo("uint8",None, False), "boneLookupIndex3":FieldTypeInfo("uint8",None, False), "normal":FieldTypeInfo("Vector4As4uint8",Vector4As4uint8, False), "uv0":FieldTypeInfo("Vector2As2int16",Vector2As2int16, False), "uv1":FieldTypeInfo("Vector2As2int16",Vector2As2int16, False), "tangent":FieldTypeInfo("Vector4As4uint8",Vector4As4uint8, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return VertexFormat0x186007d.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != VertexFormat0x186007d:
            raise Exception("%s is not of type %s but %s" % (id, "VertexFormat0x186007d", type(instance)))
        fieldId = id + ".position"

        VEC3V0.validateInstance(instance.position, fieldId)
        fieldId = id + ".boneWeight0"

        if (type(instance.boneWeight0) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".boneWeight1"

        if (type(instance.boneWeight1) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".boneWeight2"

        if (type(instance.boneWeight2) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".boneWeight3"

        if (type(instance.boneWeight3) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".boneLookupIndex0"

        if (type(instance.boneLookupIndex0) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".boneLookupIndex1"

        if (type(instance.boneLookupIndex1) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".boneLookupIndex2"

        if (type(instance.boneLookupIndex2) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".boneLookupIndex3"

        if (type(instance.boneLookupIndex3) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".normal"

        Vector4As4uint8.validateInstance(instance.normal, fieldId)
        fieldId = id + ".uv0"

        Vector2As2int16.validateInstance(instance.uv0, fieldId)
        fieldId = id + ".uv1"

        Vector2As2int16.validateInstance(instance.uv1, fieldId)
        fieldId = id + ".tangent"

        Vector4As4uint8.validateInstance(instance.tangent, fieldId)


class VertexFormat0x18e007d:
    """Vertex with three UV coordinates"""
    tagName = "VertexFormat0x18e007d"
    size = 40
    structFormat = struct.Struct("<12sBBBBBBBB4s4s4s4s4s")
    fields = ["position", "boneWeight0", "boneWeight1", "boneWeight2", "boneWeight3", "boneLookupIndex0", "boneLookupIndex1", "boneLookupIndex2", "boneLookupIndex3", "normal", "uv0", "uv1", "uv2", "tangent"]

    def __setattr__(self, name, value):
        if name in ["position", "boneWeight0", "boneWeight1", "boneWeight2", "boneWeight3", "boneLookupIndex0", "boneLookupIndex1", "boneLookupIndex2", "boneLookupIndex3", "normal", "uv0", "uv1", "uv2", "tangent"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["position", "boneWeight0", "boneWeight1", "boneWeight2", "boneWeight3", "boneLookupIndex0", "boneLookupIndex1", "boneLookupIndex2", "boneLookupIndex3", "normal", "uv0", "uv1", "uv2", "tangent"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        pass #nothing to do
    
    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        pass #nothing to do

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert VertexFormat0x18e007d.size == VertexFormat0x18e007d.structFormat.size
            rawBytes = readable.read(VertexFormat0x18e007d.size)
        if rawBytes != None:
            l = VertexFormat0x18e007d.structFormat.unpack(rawBytes)
            self.position = VEC3V0(rawBytes=l[0])
            self.boneWeight0 = l[1]
            self.boneWeight1 = l[2]
            self.boneWeight2 = l[3]
            self.boneWeight3 = l[4]
            self.boneLookupIndex0 = l[5]
            self.boneLookupIndex1 = l[6]
            self.boneLookupIndex2 = l[7]
            self.boneLookupIndex3 = l[8]
            self.normal = Vector4As4uint8(rawBytes=l[9])
            self.uv0 = Vector2As2int16(rawBytes=l[10])
            self.uv1 = Vector2As2int16(rawBytes=l[11])
            self.uv2 = Vector2As2int16(rawBytes=l[12])
            self.tangent = Vector4As4uint8(rawBytes=l[13])
        if (readable == None) and (rawBytes == None):
            self.boneWeight0 = 0
            self.boneWeight1 = 0
            self.boneWeight2 = 0
            self.boneWeight3 = 0
            self.boneLookupIndex0 = 0
            self.boneLookupIndex1 = 0
            self.boneLookupIndex2 = 0
            self.boneLookupIndex3 = 0
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + VertexFormat0x18e007d.size
        for i in range(count):
            list.append(VertexFormat0x18e007d(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += VertexFormat0x18e007d.size
        return list
    
    def toBytes(self):
        return VertexFormat0x18e007d.structFormat.pack(self.position.toBytes(), self.boneWeight0, self.boneWeight1, self.boneWeight2, self.boneWeight3, self.boneLookupIndex0, self.boneLookupIndex1, self.boneLookupIndex2, self.boneLookupIndex3, self.normal.toBytes(), self.uv0.toBytes(), self.uv1.toBytes(), self.uv2.toBytes(), self.tangent.toBytes())
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(VertexFormat0x18e007d.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = VertexFormat0x18e007d.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += VertexFormat0x18e007d.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return VertexFormat0x18e007d.countOneOrMore(object) * VertexFormat0x18e007d.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"normal": {}, "uv0": {}, "boneWeight1": {}, "uv2": {}, "boneLookupIndex0": {}, "boneWeight0": {}, "boneWeight3": {}, "boneWeight2": {}, "tangent": {}, "boneLookupIndex2": {}, "uv1": {}, "position": {}, "boneLookupIndex3": {}, "boneLookupIndex1": {}}
    
    def getNamedBit(self, field, bitName):
        mask = VertexFormat0x18e007d.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = VertexFormat0x18e007d.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return VertexFormat0x18e007d.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"position":FieldTypeInfo("VEC3V0",VEC3V0, False), "boneWeight0":FieldTypeInfo("uint8",None, False), "boneWeight1":FieldTypeInfo("uint8",None, False), "boneWeight2":FieldTypeInfo("uint8",None, False), "boneWeight3":FieldTypeInfo("uint8",None, False), "boneLookupIndex0":FieldTypeInfo("uint8",None, False), "boneLookupIndex1":FieldTypeInfo("uint8",None, False), "boneLookupIndex2":FieldTypeInfo("uint8",None, False), "boneLookupIndex3":FieldTypeInfo("uint8",None, False), "normal":FieldTypeInfo("Vector4As4uint8",Vector4As4uint8, False), "uv0":FieldTypeInfo("Vector2As2int16",Vector2As2int16, False), "uv1":FieldTypeInfo("Vector2As2int16",Vector2As2int16, False), "uv2":FieldTypeInfo("Vector2As2int16",Vector2As2int16, False), "tangent":FieldTypeInfo("Vector4As4uint8",Vector4As4uint8, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return VertexFormat0x18e007d.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != VertexFormat0x18e007d:
            raise Exception("%s is not of type %s but %s" % (id, "VertexFormat0x18e007d", type(instance)))
        fieldId = id + ".position"

        VEC3V0.validateInstance(instance.position, fieldId)
        fieldId = id + ".boneWeight0"

        if (type(instance.boneWeight0) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".boneWeight1"

        if (type(instance.boneWeight1) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".boneWeight2"

        if (type(instance.boneWeight2) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".boneWeight3"

        if (type(instance.boneWeight3) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".boneLookupIndex0"

        if (type(instance.boneLookupIndex0) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".boneLookupIndex1"

        if (type(instance.boneLookupIndex1) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".boneLookupIndex2"

        if (type(instance.boneLookupIndex2) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".boneLookupIndex3"

        if (type(instance.boneLookupIndex3) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".normal"

        Vector4As4uint8.validateInstance(instance.normal, fieldId)
        fieldId = id + ".uv0"

        Vector2As2int16.validateInstance(instance.uv0, fieldId)
        fieldId = id + ".uv1"

        Vector2As2int16.validateInstance(instance.uv1, fieldId)
        fieldId = id + ".uv2"

        Vector2As2int16.validateInstance(instance.uv2, fieldId)
        fieldId = id + ".tangent"

        Vector4As4uint8.validateInstance(instance.tangent, fieldId)


class VertexFormat0x19e007d:
    """Vertex with four UV coordinates"""
    tagName = "VertexFormat0x19e007d"
    size = 44
    structFormat = struct.Struct("<12sBBBBBBBB4s4s4s4s4s4s")
    fields = ["position", "boneWeight0", "boneWeight1", "boneWeight2", "boneWeight3", "boneLookupIndex0", "boneLookupIndex1", "boneLookupIndex2", "boneLookupIndex3", "normal", "uv0", "uv1", "uv2", "uv3", "tangent"]

    def __setattr__(self, name, value):
        if name in ["position", "boneWeight0", "boneWeight1", "boneWeight2", "boneWeight3", "boneLookupIndex0", "boneLookupIndex1", "boneLookupIndex2", "boneLookupIndex3", "normal", "uv0", "uv1", "uv2", "uv3", "tangent"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["position", "boneWeight0", "boneWeight1", "boneWeight2", "boneWeight3", "boneLookupIndex0", "boneLookupIndex1", "boneLookupIndex2", "boneLookupIndex3", "normal", "uv0", "uv1", "uv2", "uv3", "tangent"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        pass #nothing to do
    
    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        pass #nothing to do

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert VertexFormat0x19e007d.size == VertexFormat0x19e007d.structFormat.size
            rawBytes = readable.read(VertexFormat0x19e007d.size)
        if rawBytes != None:
            l = VertexFormat0x19e007d.structFormat.unpack(rawBytes)
            self.position = VEC3V0(rawBytes=l[0])
            self.boneWeight0 = l[1]
            self.boneWeight1 = l[2]
            self.boneWeight2 = l[3]
            self.boneWeight3 = l[4]
            self.boneLookupIndex0 = l[5]
            self.boneLookupIndex1 = l[6]
            self.boneLookupIndex2 = l[7]
            self.boneLookupIndex3 = l[8]
            self.normal = Vector4As4uint8(rawBytes=l[9])
            self.uv0 = Vector2As2int16(rawBytes=l[10])
            self.uv1 = Vector2As2int16(rawBytes=l[11])
            self.uv2 = Vector2As2int16(rawBytes=l[12])
            self.uv3 = Vector2As2int16(rawBytes=l[13])
            self.tangent = Vector4As4uint8(rawBytes=l[14])
        if (readable == None) and (rawBytes == None):
            self.boneWeight0 = 0
            self.boneWeight1 = 0
            self.boneWeight2 = 0
            self.boneWeight3 = 0
            self.boneLookupIndex0 = 0
            self.boneLookupIndex1 = 0
            self.boneLookupIndex2 = 0
            self.boneLookupIndex3 = 0
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + VertexFormat0x19e007d.size
        for i in range(count):
            list.append(VertexFormat0x19e007d(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += VertexFormat0x19e007d.size
        return list
    
    def toBytes(self):
        return VertexFormat0x19e007d.structFormat.pack(self.position.toBytes(), self.boneWeight0, self.boneWeight1, self.boneWeight2, self.boneWeight3, self.boneLookupIndex0, self.boneLookupIndex1, self.boneLookupIndex2, self.boneLookupIndex3, self.normal.toBytes(), self.uv0.toBytes(), self.uv1.toBytes(), self.uv2.toBytes(), self.uv3.toBytes(), self.tangent.toBytes())
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(VertexFormat0x19e007d.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = VertexFormat0x19e007d.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += VertexFormat0x19e007d.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return VertexFormat0x19e007d.countOneOrMore(object) * VertexFormat0x19e007d.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"normal": {}, "uv0": {}, "boneWeight1": {}, "uv2": {}, "uv3": {}, "boneLookupIndex0": {}, "boneWeight0": {}, "boneWeight3": {}, "boneWeight2": {}, "tangent": {}, "boneLookupIndex2": {}, "uv1": {}, "position": {}, "boneLookupIndex3": {}, "boneLookupIndex1": {}}
    
    def getNamedBit(self, field, bitName):
        mask = VertexFormat0x19e007d.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = VertexFormat0x19e007d.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return VertexFormat0x19e007d.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"position":FieldTypeInfo("VEC3V0",VEC3V0, False), "boneWeight0":FieldTypeInfo("uint8",None, False), "boneWeight1":FieldTypeInfo("uint8",None, False), "boneWeight2":FieldTypeInfo("uint8",None, False), "boneWeight3":FieldTypeInfo("uint8",None, False), "boneLookupIndex0":FieldTypeInfo("uint8",None, False), "boneLookupIndex1":FieldTypeInfo("uint8",None, False), "boneLookupIndex2":FieldTypeInfo("uint8",None, False), "boneLookupIndex3":FieldTypeInfo("uint8",None, False), "normal":FieldTypeInfo("Vector4As4uint8",Vector4As4uint8, False), "uv0":FieldTypeInfo("Vector2As2int16",Vector2As2int16, False), "uv1":FieldTypeInfo("Vector2As2int16",Vector2As2int16, False), "uv2":FieldTypeInfo("Vector2As2int16",Vector2As2int16, False), "uv3":FieldTypeInfo("Vector2As2int16",Vector2As2int16, False), "tangent":FieldTypeInfo("Vector4As4uint8",Vector4As4uint8, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return VertexFormat0x19e007d.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != VertexFormat0x19e007d:
            raise Exception("%s is not of type %s but %s" % (id, "VertexFormat0x19e007d", type(instance)))
        fieldId = id + ".position"

        VEC3V0.validateInstance(instance.position, fieldId)
        fieldId = id + ".boneWeight0"

        if (type(instance.boneWeight0) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".boneWeight1"

        if (type(instance.boneWeight1) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".boneWeight2"

        if (type(instance.boneWeight2) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".boneWeight3"

        if (type(instance.boneWeight3) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".boneLookupIndex0"

        if (type(instance.boneLookupIndex0) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".boneLookupIndex1"

        if (type(instance.boneLookupIndex1) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".boneLookupIndex2"

        if (type(instance.boneLookupIndex2) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".boneLookupIndex3"

        if (type(instance.boneLookupIndex3) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".normal"

        Vector4As4uint8.validateInstance(instance.normal, fieldId)
        fieldId = id + ".uv0"

        Vector2As2int16.validateInstance(instance.uv0, fieldId)
        fieldId = id + ".uv1"

        Vector2As2int16.validateInstance(instance.uv1, fieldId)
        fieldId = id + ".uv2"

        Vector2As2int16.validateInstance(instance.uv2, fieldId)
        fieldId = id + ".uv3"

        Vector2As2int16.validateInstance(instance.uv3, fieldId)
        fieldId = id + ".tangent"

        Vector4As4uint8.validateInstance(instance.tangent, fieldId)


class EVNTV1:
    """A sequence end event"""
    fullName = "EVNTV1"
    tagName = "EVNT"
    tagVersion = 1
    size = 104
    structFormat = struct.Struct("<12sihH64sIIIII")
    fields = ["name", "unknown0", "unknown1", "unknown2", "matrix", "unknown3", "unknown4", "unknown5", "unknown6", "missing"]

    def __setattr__(self, name, value):
        if name in ["name", "unknown0", "unknown1", "unknown2", "matrix", "unknown3", "unknown4", "unknown5", "unknown6", "missing"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["name", "unknown0", "unknown1", "unknown2", "matrix", "unknown3", "unknown4", "unknown5", "unknown6", "missing"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    def resolveReferences(self, sections):
        self.name = resolveRef(self.name,sections,CHARV0,"EVNTV1.name")


    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        if oneOrMore.__class__ == [].__class__:
            for object in oneOrMore:
                object.resolveReferences(sections) 
        else:
            oneOrMore.resolveReferences(sections)

    def introduceIndexReferences(self, indexMaker):
        indexReference = indexMaker.getIndexReferenceTo(self.name, Reference, CHARV0)
        CHARV0.introduceIndexReferencesForOneOrMore(self.name,  indexMaker)
        self.name = indexReference


    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        if object.__class__ == MD34IndexEntry:
            return # nothing to do (object was reachable trough 2 paths)
        if object.__class__ == [].__class__:
            for o in object:
                o.introduceIndexReferences(indexMaker) 
        else:
            object.introduceIndexReferences(indexMaker)

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert EVNTV1.size == EVNTV1.structFormat.size
            rawBytes = readable.read(EVNTV1.size)
        if rawBytes != None:
            l = EVNTV1.structFormat.unpack(rawBytes)
            self.name = Reference(rawBytes=l[0])
            self.unknown0 = l[1]
            if self.unknown0 != int(-1):
             raise Exception("EVNTV1.unknown0 has value %s instead of the expected value int(-1)" % self.unknown0)
            self.unknown1 = l[2]
            self.unknown2 = l[3]
            if self.unknown2 != int(0):
             raise Exception("EVNTV1.unknown2 has value %s instead of the expected value int(0)" % self.unknown2)
            self.matrix = Matrix44(rawBytes=l[4])
            self.unknown3 = l[5]
            self.unknown4 = l[6]
            if self.unknown4 != int(0):
             raise Exception("EVNTV1.unknown4 has value %s instead of the expected value int(0)" % self.unknown4)
            self.unknown5 = l[7]
            if self.unknown5 != int(0):
             raise Exception("EVNTV1.unknown5 has value %s instead of the expected value int(0)" % self.unknown5)
            self.unknown6 = l[8]
            if self.unknown6 != int(0):
             raise Exception("EVNTV1.unknown6 has value %s instead of the expected value int(0)" % self.unknown6)
            self.missing = l[9]
            if self.missing != int(0):
             raise Exception("EVNTV1.missing has value %s instead of the expected value int(0)" % self.missing)
        if (readable == None) and (rawBytes == None):
            self.name = CHARV0.createEmptyArray()
            self.unknown0 = int(-1)
            self.unknown1 = -1
            self.unknown2 = int(0)
            self.unknown3 = 4
            self.unknown4 = int(0)
            self.unknown5 = int(0)
            self.unknown6 = int(0)
            self.missing = int(0)
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + EVNTV1.size
        for i in range(count):
            list.append(EVNTV1(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += EVNTV1.size
        return list
    
    def toBytes(self):
        return EVNTV1.structFormat.pack(self.name.toBytes(), self.unknown0, self.unknown1, self.unknown2, self.matrix.toBytes(), self.unknown3, self.unknown4, self.unknown5, self.unknown6, self.missing)
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(EVNTV1.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = EVNTV1.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += EVNTV1.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return EVNTV1.countOneOrMore(object) * EVNTV1.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"name": {}, "missing": {}, "unknown2": {}, "unknown3": {}, "unknown0": {}, "unknown1": {}, "unknown6": {}, "unknown4": {}, "unknown5": {}, "matrix": {}}
    
    def getNamedBit(self, field, bitName):
        mask = EVNTV1.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = EVNTV1.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return EVNTV1.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"name":FieldTypeInfo("CHARV0",CHARV0, True), "unknown0":FieldTypeInfo("int32",None, False), "unknown1":FieldTypeInfo("int16",None, False), "unknown2":FieldTypeInfo("uint16",None, False), "matrix":FieldTypeInfo("Matrix44",Matrix44, False), "unknown3":FieldTypeInfo("uint32",None, False), "unknown4":FieldTypeInfo("uint32",None, False), "unknown5":FieldTypeInfo("uint32",None, False), "unknown6":FieldTypeInfo("uint32",None, False), "missing":FieldTypeInfo("uint32",None, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return EVNTV1.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != EVNTV1:
            raise Exception("%s is not of type %s but %s" % (id, "EVNTV1", type(instance)))
        fieldId = id + ".name"

        if (instance.name != None) and (type(instance.name) != str):
            raise Exception("%s is not a string but a %s" % (fieldId, type(instance.name) ))
        fieldId = id + ".unknown0"

        if (type(instance.unknown0) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".unknown1"

        if (type(instance.unknown1) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".unknown2"

        if (type(instance.unknown2) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".matrix"

        Matrix44.validateInstance(instance.matrix, fieldId)
        fieldId = id + ".unknown3"

        if (type(instance.unknown3) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".unknown4"

        if (type(instance.unknown4) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".unknown5"

        if (type(instance.unknown5) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".unknown6"

        if (type(instance.unknown6) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".missing"

        if (type(instance.missing) != int):
            raise Exception("%s is not an int" % (fieldId))


class FLAGV0:
    """A flag used by animations"""
    fullName = "FLAGV0"
    tagName = "FLAG"
    tagVersion = 0
    size = 4
    structFormat = struct.Struct("<I")
    fields = ["value"]

    def __setattr__(self, name, value):
        if name in ["value"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["value"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        pass #nothing to do
    
    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        pass #nothing to do

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert FLAGV0.size == FLAGV0.structFormat.size
            rawBytes = readable.read(FLAGV0.size)
        if rawBytes != None:
            l = FLAGV0.structFormat.unpack(rawBytes)
            self.value = l[0]
        if (readable == None) and (rawBytes == None):
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + FLAGV0.size
        for i in range(count):
            list.append(FLAGV0(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += FLAGV0.size
        return list
    
    def toBytes(self):
        return FLAGV0.structFormat.pack(self.value)
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(FLAGV0.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = FLAGV0.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += FLAGV0.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return FLAGV0.countOneOrMore(object) * FLAGV0.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"value": {}}
    
    def getNamedBit(self, field, bitName):
        mask = FLAGV0.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = FLAGV0.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return FLAGV0.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"value":FieldTypeInfo("uint32",None, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return FLAGV0.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != FLAGV0:
            raise Exception("%s is not of type %s but %s" % (id, "FLAGV0", type(instance)))
        fieldId = id + ".value"

        if (type(instance.value) != int):
            raise Exception("%s is not an int" % (fieldId))


class SDEVV0:
    """Event Key FramesAnimation block with reference to EVNT"""
    fullName = "SDEVV0"
    tagName = "SDEV"
    tagVersion = 0
    size = 32
    structFormat = struct.Struct("<12sII12s")
    fields = ["frames", "flags", "fend", "keys"]

    def __setattr__(self, name, value):
        if name in ["frames", "flags", "fend", "keys"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["frames", "flags", "fend", "keys"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    def resolveReferences(self, sections):
        self.frames = resolveRef(self.frames,sections,I32_V0,"SDEVV0.frames")
        self.keys = resolveRef(self.keys,sections,EVNTV1,"SDEVV0.keys")


    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        if oneOrMore.__class__ == [].__class__:
            for object in oneOrMore:
                object.resolveReferences(sections) 
        else:
            oneOrMore.resolveReferences(sections)

    def introduceIndexReferences(self, indexMaker):
        indexReference = indexMaker.getIndexReferenceTo(self.frames, Reference, I32_V0)
        I32_V0.introduceIndexReferencesForOneOrMore(self.frames,  indexMaker)
        self.frames = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.keys, Reference, EVNTV1)
        EVNTV1.introduceIndexReferencesForOneOrMore(self.keys,  indexMaker)
        self.keys = indexReference


    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        if object.__class__ == MD34IndexEntry:
            return # nothing to do (object was reachable trough 2 paths)
        if object.__class__ == [].__class__:
            for o in object:
                o.introduceIndexReferences(indexMaker) 
        else:
            object.introduceIndexReferences(indexMaker)

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert SDEVV0.size == SDEVV0.structFormat.size
            rawBytes = readable.read(SDEVV0.size)
        if rawBytes != None:
            l = SDEVV0.structFormat.unpack(rawBytes)
            self.frames = Reference(rawBytes=l[0])
            self.flags = l[1]
            self.fend = l[2]
            self.keys = Reference(rawBytes=l[3])
        if (readable == None) and (rawBytes == None):
            self.frames = I32_V0.createEmptyArray()
            self.keys = EVNTV1.createEmptyArray()
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + SDEVV0.size
        for i in range(count):
            list.append(SDEVV0(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += SDEVV0.size
        return list
    
    def toBytes(self):
        return SDEVV0.structFormat.pack(self.frames.toBytes(), self.flags, self.fend, self.keys.toBytes())
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(SDEVV0.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = SDEVV0.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += SDEVV0.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return SDEVV0.countOneOrMore(object) * SDEVV0.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"frames": {}, "fend": {}, "keys": {}, "flags": {}}
    
    def getNamedBit(self, field, bitName):
        mask = SDEVV0.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = SDEVV0.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return SDEVV0.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"frames":FieldTypeInfo("I32_V0",I32_V0, True), "flags":FieldTypeInfo("uint32",None, False), "fend":FieldTypeInfo("uint32",None, False), "keys":FieldTypeInfo("EVNTV1",EVNTV1, True)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return SDEVV0.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != SDEVV0:
            raise Exception("%s is not of type %s but %s" % (id, "SDEVV0", type(instance)))
        fieldId = id + ".frames"
        if (type(instance.frames) != list):
            raise Exception("%s is not a list of integers" % (fieldId))
        for itemIndex, item in enumerate(instance.frames):
            itemId = "%s[%d]" % (fieldId, itemIndex)
            if type(item) != int: 
                raise Exception("%s is not an integer" % (itemId))
            if (item < -4294967296) or (item > 4294967295):
                raise Exception("%s has value %d which is not in range [-4294967296, 4294967295]"  % (itemId, item))
        fieldId = id + ".flags"

        if (type(instance.flags) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".fend"

        if (type(instance.fend) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".keys"

        if (type(instance.keys) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "EVNTV1", type(instance.keys)))
        for itemIndex, item in enumerate(instance.keys):
            EVNTV1.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))


class SD2VV0:
    """Vector 2 Animation block with reference to VEC2"""
    fullName = "SD2VV0"
    tagName = "SD2V"
    tagVersion = 0
    size = 32
    structFormat = struct.Struct("<12sII12s")
    fields = ["frames", "flags", "fend", "keys"]

    def __setattr__(self, name, value):
        if name in ["frames", "flags", "fend", "keys"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["frames", "flags", "fend", "keys"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    def resolveReferences(self, sections):
        self.frames = resolveRef(self.frames,sections,I32_V0,"SD2VV0.frames")
        self.keys = resolveRef(self.keys,sections,VEC2V0,"SD2VV0.keys")


    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        if oneOrMore.__class__ == [].__class__:
            for object in oneOrMore:
                object.resolveReferences(sections) 
        else:
            oneOrMore.resolveReferences(sections)

    def introduceIndexReferences(self, indexMaker):
        indexReference = indexMaker.getIndexReferenceTo(self.frames, Reference, I32_V0)
        I32_V0.introduceIndexReferencesForOneOrMore(self.frames,  indexMaker)
        self.frames = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.keys, Reference, VEC2V0)
        VEC2V0.introduceIndexReferencesForOneOrMore(self.keys,  indexMaker)
        self.keys = indexReference


    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        if object.__class__ == MD34IndexEntry:
            return # nothing to do (object was reachable trough 2 paths)
        if object.__class__ == [].__class__:
            for o in object:
                o.introduceIndexReferences(indexMaker) 
        else:
            object.introduceIndexReferences(indexMaker)

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert SD2VV0.size == SD2VV0.structFormat.size
            rawBytes = readable.read(SD2VV0.size)
        if rawBytes != None:
            l = SD2VV0.structFormat.unpack(rawBytes)
            self.frames = Reference(rawBytes=l[0])
            self.flags = l[1]
            self.fend = l[2]
            self.keys = Reference(rawBytes=l[3])
        if (readable == None) and (rawBytes == None):
            self.frames = I32_V0.createEmptyArray()
            self.keys = VEC2V0.createEmptyArray()
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + SD2VV0.size
        for i in range(count):
            list.append(SD2VV0(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += SD2VV0.size
        return list
    
    def toBytes(self):
        return SD2VV0.structFormat.pack(self.frames.toBytes(), self.flags, self.fend, self.keys.toBytes())
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(SD2VV0.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = SD2VV0.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += SD2VV0.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return SD2VV0.countOneOrMore(object) * SD2VV0.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"frames": {}, "fend": {}, "keys": {}, "flags": {}}
    
    def getNamedBit(self, field, bitName):
        mask = SD2VV0.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = SD2VV0.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return SD2VV0.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"frames":FieldTypeInfo("I32_V0",I32_V0, True), "flags":FieldTypeInfo("uint32",None, False), "fend":FieldTypeInfo("uint32",None, False), "keys":FieldTypeInfo("VEC2V0",VEC2V0, True)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return SD2VV0.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != SD2VV0:
            raise Exception("%s is not of type %s but %s" % (id, "SD2VV0", type(instance)))
        fieldId = id + ".frames"
        if (type(instance.frames) != list):
            raise Exception("%s is not a list of integers" % (fieldId))
        for itemIndex, item in enumerate(instance.frames):
            itemId = "%s[%d]" % (fieldId, itemIndex)
            if type(item) != int: 
                raise Exception("%s is not an integer" % (itemId))
            if (item < -4294967296) or (item > 4294967295):
                raise Exception("%s has value %d which is not in range [-4294967296, 4294967295]"  % (itemId, item))
        fieldId = id + ".flags"

        if (type(instance.flags) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".fend"

        if (type(instance.fend) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".keys"

        if (type(instance.keys) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "VEC2V0", type(instance.keys)))
        for itemIndex, item in enumerate(instance.keys):
            VEC2V0.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))


class SD3VV0:
    """Vector 3 Animation block with reference to VEC3"""
    fullName = "SD3VV0"
    tagName = "SD3V"
    tagVersion = 0
    size = 32
    structFormat = struct.Struct("<12sII12s")
    fields = ["frames", "flags", "fend", "keys"]

    def __setattr__(self, name, value):
        if name in ["frames", "flags", "fend", "keys"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["frames", "flags", "fend", "keys"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    def resolveReferences(self, sections):
        self.frames = resolveRef(self.frames,sections,I32_V0,"SD3VV0.frames")
        self.keys = resolveRef(self.keys,sections,VEC3V0,"SD3VV0.keys")


    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        if oneOrMore.__class__ == [].__class__:
            for object in oneOrMore:
                object.resolveReferences(sections) 
        else:
            oneOrMore.resolveReferences(sections)

    def introduceIndexReferences(self, indexMaker):
        indexReference = indexMaker.getIndexReferenceTo(self.frames, Reference, I32_V0)
        I32_V0.introduceIndexReferencesForOneOrMore(self.frames,  indexMaker)
        self.frames = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.keys, Reference, VEC3V0)
        VEC3V0.introduceIndexReferencesForOneOrMore(self.keys,  indexMaker)
        self.keys = indexReference


    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        if object.__class__ == MD34IndexEntry:
            return # nothing to do (object was reachable trough 2 paths)
        if object.__class__ == [].__class__:
            for o in object:
                o.introduceIndexReferences(indexMaker) 
        else:
            object.introduceIndexReferences(indexMaker)

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert SD3VV0.size == SD3VV0.structFormat.size
            rawBytes = readable.read(SD3VV0.size)
        if rawBytes != None:
            l = SD3VV0.structFormat.unpack(rawBytes)
            self.frames = Reference(rawBytes=l[0])
            self.flags = l[1]
            self.fend = l[2]
            self.keys = Reference(rawBytes=l[3])
        if (readable == None) and (rawBytes == None):
            self.frames = I32_V0.createEmptyArray()
            self.keys = VEC3V0.createEmptyArray()
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + SD3VV0.size
        for i in range(count):
            list.append(SD3VV0(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += SD3VV0.size
        return list
    
    def toBytes(self):
        return SD3VV0.structFormat.pack(self.frames.toBytes(), self.flags, self.fend, self.keys.toBytes())
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(SD3VV0.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = SD3VV0.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += SD3VV0.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return SD3VV0.countOneOrMore(object) * SD3VV0.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"frames": {}, "fend": {}, "keys": {}, "flags": {}}
    
    def getNamedBit(self, field, bitName):
        mask = SD3VV0.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = SD3VV0.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return SD3VV0.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"frames":FieldTypeInfo("I32_V0",I32_V0, True), "flags":FieldTypeInfo("uint32",None, False), "fend":FieldTypeInfo("uint32",None, False), "keys":FieldTypeInfo("VEC3V0",VEC3V0, True)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return SD3VV0.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != SD3VV0:
            raise Exception("%s is not of type %s but %s" % (id, "SD3VV0", type(instance)))
        fieldId = id + ".frames"
        if (type(instance.frames) != list):
            raise Exception("%s is not a list of integers" % (fieldId))
        for itemIndex, item in enumerate(instance.frames):
            itemId = "%s[%d]" % (fieldId, itemIndex)
            if type(item) != int: 
                raise Exception("%s is not an integer" % (itemId))
            if (item < -4294967296) or (item > 4294967295):
                raise Exception("%s has value %d which is not in range [-4294967296, 4294967295]"  % (itemId, item))
        fieldId = id + ".flags"

        if (type(instance.flags) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".fend"

        if (type(instance.fend) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".keys"

        if (type(instance.keys) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "VEC3V0", type(instance.keys)))
        for itemIndex, item in enumerate(instance.keys):
            VEC3V0.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))


class SDR3V0:
    """Animation block with reference to REAL(float array)"""
    fullName = "SDR3V0"
    tagName = "SDR3"
    tagVersion = 0
    size = 32
    structFormat = struct.Struct("<12sII12s")
    fields = ["frames", "flags", "fend", "keys"]

    def __setattr__(self, name, value):
        if name in ["frames", "flags", "fend", "keys"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["frames", "flags", "fend", "keys"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    def resolveReferences(self, sections):
        self.frames = resolveRef(self.frames,sections,I32_V0,"SDR3V0.frames")
        self.keys = resolveRef(self.keys,sections,REALV0,"SDR3V0.keys")


    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        if oneOrMore.__class__ == [].__class__:
            for object in oneOrMore:
                object.resolveReferences(sections) 
        else:
            oneOrMore.resolveReferences(sections)

    def introduceIndexReferences(self, indexMaker):
        indexReference = indexMaker.getIndexReferenceTo(self.frames, Reference, I32_V0)
        I32_V0.introduceIndexReferencesForOneOrMore(self.frames,  indexMaker)
        self.frames = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.keys, Reference, REALV0)
        REALV0.introduceIndexReferencesForOneOrMore(self.keys,  indexMaker)
        self.keys = indexReference


    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        if object.__class__ == MD34IndexEntry:
            return # nothing to do (object was reachable trough 2 paths)
        if object.__class__ == [].__class__:
            for o in object:
                o.introduceIndexReferences(indexMaker) 
        else:
            object.introduceIndexReferences(indexMaker)

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert SDR3V0.size == SDR3V0.structFormat.size
            rawBytes = readable.read(SDR3V0.size)
        if rawBytes != None:
            l = SDR3V0.structFormat.unpack(rawBytes)
            self.frames = Reference(rawBytes=l[0])
            self.flags = l[1]
            self.fend = l[2]
            self.keys = Reference(rawBytes=l[3])
        if (readable == None) and (rawBytes == None):
            self.frames = I32_V0.createEmptyArray()
            self.keys = REALV0.createEmptyArray()
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + SDR3V0.size
        for i in range(count):
            list.append(SDR3V0(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += SDR3V0.size
        return list
    
    def toBytes(self):
        return SDR3V0.structFormat.pack(self.frames.toBytes(), self.flags, self.fend, self.keys.toBytes())
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(SDR3V0.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = SDR3V0.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += SDR3V0.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return SDR3V0.countOneOrMore(object) * SDR3V0.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"frames": {}, "fend": {}, "keys": {}, "flags": {}}
    
    def getNamedBit(self, field, bitName):
        mask = SDR3V0.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = SDR3V0.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return SDR3V0.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"frames":FieldTypeInfo("I32_V0",I32_V0, True), "flags":FieldTypeInfo("uint32",None, False), "fend":FieldTypeInfo("uint32",None, False), "keys":FieldTypeInfo("REALV0",REALV0, True)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return SDR3V0.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != SDR3V0:
            raise Exception("%s is not of type %s but %s" % (id, "SDR3V0", type(instance)))
        fieldId = id + ".frames"
        if (type(instance.frames) != list):
            raise Exception("%s is not a list of integers" % (fieldId))
        for itemIndex, item in enumerate(instance.frames):
            itemId = "%s[%d]" % (fieldId, itemIndex)
            if type(item) != int: 
                raise Exception("%s is not an integer" % (itemId))
            if (item < -4294967296) or (item > 4294967295):
                raise Exception("%s has value %d which is not in range [-4294967296, 4294967295]"  % (itemId, item))
        fieldId = id + ".flags"

        if (type(instance.flags) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".fend"

        if (type(instance.fend) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".keys"

        if (type(instance.keys) != list):            raise Exception("%s is not a list of float" % (fieldId))
        for itemIndex, item in enumerate(instance.keys):
            if type(item) != float: 
                itemId = "%s[%d]" % (fieldId, itemIndex)
                raise Exception("%s is not an float" % (itemId))


class SDCCV0:
    """Animation block with reference to COL (Color)"""
    fullName = "SDCCV0"
    tagName = "SDCC"
    tagVersion = 0
    size = 32
    structFormat = struct.Struct("<12sII12s")
    fields = ["frames", "flags", "fend", "keys"]

    def __setattr__(self, name, value):
        if name in ["frames", "flags", "fend", "keys"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["frames", "flags", "fend", "keys"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    def resolveReferences(self, sections):
        self.frames = resolveRef(self.frames,sections,I32_V0,"SDCCV0.frames")
        self.keys = resolveRef(self.keys,sections,COLV0,"SDCCV0.keys")


    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        if oneOrMore.__class__ == [].__class__:
            for object in oneOrMore:
                object.resolveReferences(sections) 
        else:
            oneOrMore.resolveReferences(sections)

    def introduceIndexReferences(self, indexMaker):
        indexReference = indexMaker.getIndexReferenceTo(self.frames, Reference, I32_V0)
        I32_V0.introduceIndexReferencesForOneOrMore(self.frames,  indexMaker)
        self.frames = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.keys, Reference, COLV0)
        COLV0.introduceIndexReferencesForOneOrMore(self.keys,  indexMaker)
        self.keys = indexReference


    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        if object.__class__ == MD34IndexEntry:
            return # nothing to do (object was reachable trough 2 paths)
        if object.__class__ == [].__class__:
            for o in object:
                o.introduceIndexReferences(indexMaker) 
        else:
            object.introduceIndexReferences(indexMaker)

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert SDCCV0.size == SDCCV0.structFormat.size
            rawBytes = readable.read(SDCCV0.size)
        if rawBytes != None:
            l = SDCCV0.structFormat.unpack(rawBytes)
            self.frames = Reference(rawBytes=l[0])
            self.flags = l[1]
            self.fend = l[2]
            self.keys = Reference(rawBytes=l[3])
        if (readable == None) and (rawBytes == None):
            self.frames = I32_V0.createEmptyArray()
            self.keys = COLV0.createEmptyArray()
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + SDCCV0.size
        for i in range(count):
            list.append(SDCCV0(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += SDCCV0.size
        return list
    
    def toBytes(self):
        return SDCCV0.structFormat.pack(self.frames.toBytes(), self.flags, self.fend, self.keys.toBytes())
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(SDCCV0.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = SDCCV0.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += SDCCV0.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return SDCCV0.countOneOrMore(object) * SDCCV0.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"frames": {}, "fend": {}, "keys": {}, "flags": {}}
    
    def getNamedBit(self, field, bitName):
        mask = SDCCV0.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = SDCCV0.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return SDCCV0.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"frames":FieldTypeInfo("I32_V0",I32_V0, True), "flags":FieldTypeInfo("uint32",None, False), "fend":FieldTypeInfo("uint32",None, False), "keys":FieldTypeInfo("COLV0",COLV0, True)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return SDCCV0.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != SDCCV0:
            raise Exception("%s is not of type %s but %s" % (id, "SDCCV0", type(instance)))
        fieldId = id + ".frames"
        if (type(instance.frames) != list):
            raise Exception("%s is not a list of integers" % (fieldId))
        for itemIndex, item in enumerate(instance.frames):
            itemId = "%s[%d]" % (fieldId, itemIndex)
            if type(item) != int: 
                raise Exception("%s is not an integer" % (itemId))
            if (item < -4294967296) or (item > 4294967295):
                raise Exception("%s has value %d which is not in range [-4294967296, 4294967295]"  % (itemId, item))
        fieldId = id + ".flags"

        if (type(instance.flags) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".fend"

        if (type(instance.fend) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".keys"

        if (type(instance.keys) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "COLV0", type(instance.keys)))
        for itemIndex, item in enumerate(instance.keys):
            COLV0.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))


class SDS6V0:
    """Animation block with reference to I16_"""
    fullName = "SDS6V0"
    tagName = "SDS6"
    tagVersion = 0
    size = 32
    structFormat = struct.Struct("<12sII12s")
    fields = ["frames", "flags", "fend", "keys"]

    def __setattr__(self, name, value):
        if name in ["frames", "flags", "fend", "keys"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["frames", "flags", "fend", "keys"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    def resolveReferences(self, sections):
        self.frames = resolveRef(self.frames,sections,I32_V0,"SDS6V0.frames")
        self.keys = resolveRef(self.keys,sections,I16_V0,"SDS6V0.keys")


    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        if oneOrMore.__class__ == [].__class__:
            for object in oneOrMore:
                object.resolveReferences(sections) 
        else:
            oneOrMore.resolveReferences(sections)

    def introduceIndexReferences(self, indexMaker):
        indexReference = indexMaker.getIndexReferenceTo(self.frames, Reference, I32_V0)
        I32_V0.introduceIndexReferencesForOneOrMore(self.frames,  indexMaker)
        self.frames = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.keys, Reference, I16_V0)
        I16_V0.introduceIndexReferencesForOneOrMore(self.keys,  indexMaker)
        self.keys = indexReference


    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        if object.__class__ == MD34IndexEntry:
            return # nothing to do (object was reachable trough 2 paths)
        if object.__class__ == [].__class__:
            for o in object:
                o.introduceIndexReferences(indexMaker) 
        else:
            object.introduceIndexReferences(indexMaker)

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert SDS6V0.size == SDS6V0.structFormat.size
            rawBytes = readable.read(SDS6V0.size)
        if rawBytes != None:
            l = SDS6V0.structFormat.unpack(rawBytes)
            self.frames = Reference(rawBytes=l[0])
            self.flags = l[1]
            self.fend = l[2]
            self.keys = Reference(rawBytes=l[3])
        if (readable == None) and (rawBytes == None):
            self.frames = I32_V0.createEmptyArray()
            self.keys = I16_V0.createEmptyArray()
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + SDS6V0.size
        for i in range(count):
            list.append(SDS6V0(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += SDS6V0.size
        return list
    
    def toBytes(self):
        return SDS6V0.structFormat.pack(self.frames.toBytes(), self.flags, self.fend, self.keys.toBytes())
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(SDS6V0.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = SDS6V0.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += SDS6V0.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return SDS6V0.countOneOrMore(object) * SDS6V0.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"frames": {}, "fend": {}, "keys": {}, "flags": {}}
    
    def getNamedBit(self, field, bitName):
        mask = SDS6V0.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = SDS6V0.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return SDS6V0.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"frames":FieldTypeInfo("I32_V0",I32_V0, True), "flags":FieldTypeInfo("uint32",None, False), "fend":FieldTypeInfo("uint32",None, False), "keys":FieldTypeInfo("I16_V0",I16_V0, True)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return SDS6V0.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != SDS6V0:
            raise Exception("%s is not of type %s but %s" % (id, "SDS6V0", type(instance)))
        fieldId = id + ".frames"
        if (type(instance.frames) != list):
            raise Exception("%s is not a list of integers" % (fieldId))
        for itemIndex, item in enumerate(instance.frames):
            itemId = "%s[%d]" % (fieldId, itemIndex)
            if type(item) != int: 
                raise Exception("%s is not an integer" % (itemId))
            if (item < -4294967296) or (item > 4294967295):
                raise Exception("%s has value %d which is not in range [-4294967296, 4294967295]"  % (itemId, item))
        fieldId = id + ".flags"

        if (type(instance.flags) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".fend"

        if (type(instance.fend) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".keys"
        if (type(instance.keys) != list):
            raise Exception("%s is not a list of integers" % (fieldId))
        for itemIndex, item in enumerate(instance.keys):
            itemId = "%s[%d]" % (fieldId, itemIndex)
            if type(item) != int: 
                raise Exception("%s is not an integer" % (itemId))
            if (item < -65536) or (item > 65535):
                raise Exception("%s has value %d which is not in range [-65536, 65535]"  % (itemId, item))


class SDU6V0:
    """Animation block with reference to U16_"""
    fullName = "SDU6V0"
    tagName = "SDU6"
    tagVersion = 0
    size = 32
    structFormat = struct.Struct("<12sII12s")
    fields = ["frames", "flags", "fend", "keys"]

    def __setattr__(self, name, value):
        if name in ["frames", "flags", "fend", "keys"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["frames", "flags", "fend", "keys"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    def resolveReferences(self, sections):
        self.frames = resolveRef(self.frames,sections,I32_V0,"SDU6V0.frames")
        self.keys = resolveRef(self.keys,sections,U16_V0,"SDU6V0.keys")


    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        if oneOrMore.__class__ == [].__class__:
            for object in oneOrMore:
                object.resolveReferences(sections) 
        else:
            oneOrMore.resolveReferences(sections)

    def introduceIndexReferences(self, indexMaker):
        indexReference = indexMaker.getIndexReferenceTo(self.frames, Reference, I32_V0)
        I32_V0.introduceIndexReferencesForOneOrMore(self.frames,  indexMaker)
        self.frames = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.keys, Reference, U16_V0)
        U16_V0.introduceIndexReferencesForOneOrMore(self.keys,  indexMaker)
        self.keys = indexReference


    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        if object.__class__ == MD34IndexEntry:
            return # nothing to do (object was reachable trough 2 paths)
        if object.__class__ == [].__class__:
            for o in object:
                o.introduceIndexReferences(indexMaker) 
        else:
            object.introduceIndexReferences(indexMaker)

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert SDU6V0.size == SDU6V0.structFormat.size
            rawBytes = readable.read(SDU6V0.size)
        if rawBytes != None:
            l = SDU6V0.structFormat.unpack(rawBytes)
            self.frames = Reference(rawBytes=l[0])
            self.flags = l[1]
            self.fend = l[2]
            self.keys = Reference(rawBytes=l[3])
        if (readable == None) and (rawBytes == None):
            self.frames = I32_V0.createEmptyArray()
            self.keys = U16_V0.createEmptyArray()
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + SDU6V0.size
        for i in range(count):
            list.append(SDU6V0(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += SDU6V0.size
        return list
    
    def toBytes(self):
        return SDU6V0.structFormat.pack(self.frames.toBytes(), self.flags, self.fend, self.keys.toBytes())
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(SDU6V0.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = SDU6V0.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += SDU6V0.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return SDU6V0.countOneOrMore(object) * SDU6V0.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"frames": {}, "fend": {}, "keys": {}, "flags": {}}
    
    def getNamedBit(self, field, bitName):
        mask = SDU6V0.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = SDU6V0.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return SDU6V0.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"frames":FieldTypeInfo("I32_V0",I32_V0, True), "flags":FieldTypeInfo("uint32",None, False), "fend":FieldTypeInfo("uint32",None, False), "keys":FieldTypeInfo("U16_V0",U16_V0, True)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return SDU6V0.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != SDU6V0:
            raise Exception("%s is not of type %s but %s" % (id, "SDU6V0", type(instance)))
        fieldId = id + ".frames"
        if (type(instance.frames) != list):
            raise Exception("%s is not a list of integers" % (fieldId))
        for itemIndex, item in enumerate(instance.frames):
            itemId = "%s[%d]" % (fieldId, itemIndex)
            if type(item) != int: 
                raise Exception("%s is not an integer" % (itemId))
            if (item < -4294967296) or (item > 4294967295):
                raise Exception("%s has value %d which is not in range [-4294967296, 4294967295]"  % (itemId, item))
        fieldId = id + ".flags"

        if (type(instance.flags) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".fend"

        if (type(instance.fend) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".keys"
        if (type(instance.keys) != list):
            raise Exception("%s is not a list of integers" % (fieldId))
        for itemIndex, item in enumerate(instance.keys):
            itemId = "%s[%d]" % (fieldId, itemIndex)
            if type(item) != int: 
                raise Exception("%s is not an integer" % (itemId))
            if (item < 0) or (item > 131071):
                raise Exception("%s has value %d which is not in range [0, 131071]"  % (itemId, item))


class SD4QV0:
    """Animation block with reference to QUAT"""
    fullName = "SD4QV0"
    tagName = "SD4Q"
    tagVersion = 0
    size = 32
    structFormat = struct.Struct("<12sII12s")
    fields = ["frames", "flags", "fend", "keys"]

    def __setattr__(self, name, value):
        if name in ["frames", "flags", "fend", "keys"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["frames", "flags", "fend", "keys"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    def resolveReferences(self, sections):
        self.frames = resolveRef(self.frames,sections,I32_V0,"SD4QV0.frames")
        self.keys = resolveRef(self.keys,sections,QUATV0,"SD4QV0.keys")


    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        if oneOrMore.__class__ == [].__class__:
            for object in oneOrMore:
                object.resolveReferences(sections) 
        else:
            oneOrMore.resolveReferences(sections)

    def introduceIndexReferences(self, indexMaker):
        indexReference = indexMaker.getIndexReferenceTo(self.frames, Reference, I32_V0)
        I32_V0.introduceIndexReferencesForOneOrMore(self.frames,  indexMaker)
        self.frames = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.keys, Reference, QUATV0)
        QUATV0.introduceIndexReferencesForOneOrMore(self.keys,  indexMaker)
        self.keys = indexReference


    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        if object.__class__ == MD34IndexEntry:
            return # nothing to do (object was reachable trough 2 paths)
        if object.__class__ == [].__class__:
            for o in object:
                o.introduceIndexReferences(indexMaker) 
        else:
            object.introduceIndexReferences(indexMaker)

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert SD4QV0.size == SD4QV0.structFormat.size
            rawBytes = readable.read(SD4QV0.size)
        if rawBytes != None:
            l = SD4QV0.structFormat.unpack(rawBytes)
            self.frames = Reference(rawBytes=l[0])
            self.flags = l[1]
            self.fend = l[2]
            self.keys = Reference(rawBytes=l[3])
        if (readable == None) and (rawBytes == None):
            self.frames = I32_V0.createEmptyArray()
            self.keys = QUATV0.createEmptyArray()
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + SD4QV0.size
        for i in range(count):
            list.append(SD4QV0(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += SD4QV0.size
        return list
    
    def toBytes(self):
        return SD4QV0.structFormat.pack(self.frames.toBytes(), self.flags, self.fend, self.keys.toBytes())
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(SD4QV0.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = SD4QV0.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += SD4QV0.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return SD4QV0.countOneOrMore(object) * SD4QV0.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"frames": {}, "fend": {}, "keys": {}, "flags": {}}
    
    def getNamedBit(self, field, bitName):
        mask = SD4QV0.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = SD4QV0.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return SD4QV0.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"frames":FieldTypeInfo("I32_V0",I32_V0, True), "flags":FieldTypeInfo("uint32",None, False), "fend":FieldTypeInfo("uint32",None, False), "keys":FieldTypeInfo("QUATV0",QUATV0, True)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return SD4QV0.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != SD4QV0:
            raise Exception("%s is not of type %s but %s" % (id, "SD4QV0", type(instance)))
        fieldId = id + ".frames"
        if (type(instance.frames) != list):
            raise Exception("%s is not a list of integers" % (fieldId))
        for itemIndex, item in enumerate(instance.frames):
            itemId = "%s[%d]" % (fieldId, itemIndex)
            if type(item) != int: 
                raise Exception("%s is not an integer" % (itemId))
            if (item < -4294967296) or (item > 4294967295):
                raise Exception("%s has value %d which is not in range [-4294967296, 4294967295]"  % (itemId, item))
        fieldId = id + ".flags"

        if (type(instance.flags) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".fend"

        if (type(instance.fend) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".keys"

        if (type(instance.keys) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "QUATV0", type(instance.keys)))
        for itemIndex, item in enumerate(instance.keys):
            QUATV0.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))


class SDFGV0:
    """Animation block with reference to FLAG"""
    fullName = "SDFGV0"
    tagName = "SDFG"
    tagVersion = 0
    size = 32
    structFormat = struct.Struct("<12sII12s")
    fields = ["frames", "flags", "fend", "keys"]

    def __setattr__(self, name, value):
        if name in ["frames", "flags", "fend", "keys"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["frames", "flags", "fend", "keys"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    def resolveReferences(self, sections):
        self.frames = resolveRef(self.frames,sections,I32_V0,"SDFGV0.frames")
        self.keys = resolveRef(self.keys,sections,FLAGV0,"SDFGV0.keys")


    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        if oneOrMore.__class__ == [].__class__:
            for object in oneOrMore:
                object.resolveReferences(sections) 
        else:
            oneOrMore.resolveReferences(sections)

    def introduceIndexReferences(self, indexMaker):
        indexReference = indexMaker.getIndexReferenceTo(self.frames, Reference, I32_V0)
        I32_V0.introduceIndexReferencesForOneOrMore(self.frames,  indexMaker)
        self.frames = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.keys, Reference, FLAGV0)
        FLAGV0.introduceIndexReferencesForOneOrMore(self.keys,  indexMaker)
        self.keys = indexReference


    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        if object.__class__ == MD34IndexEntry:
            return # nothing to do (object was reachable trough 2 paths)
        if object.__class__ == [].__class__:
            for o in object:
                o.introduceIndexReferences(indexMaker) 
        else:
            object.introduceIndexReferences(indexMaker)

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert SDFGV0.size == SDFGV0.structFormat.size
            rawBytes = readable.read(SDFGV0.size)
        if rawBytes != None:
            l = SDFGV0.structFormat.unpack(rawBytes)
            self.frames = Reference(rawBytes=l[0])
            self.flags = l[1]
            self.fend = l[2]
            self.keys = Reference(rawBytes=l[3])
        if (readable == None) and (rawBytes == None):
            self.frames = I32_V0.createEmptyArray()
            self.keys = FLAGV0.createEmptyArray()
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + SDFGV0.size
        for i in range(count):
            list.append(SDFGV0(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += SDFGV0.size
        return list
    
    def toBytes(self):
        return SDFGV0.structFormat.pack(self.frames.toBytes(), self.flags, self.fend, self.keys.toBytes())
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(SDFGV0.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = SDFGV0.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += SDFGV0.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return SDFGV0.countOneOrMore(object) * SDFGV0.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"frames": {}, "fend": {}, "keys": {}, "flags": {}}
    
    def getNamedBit(self, field, bitName):
        mask = SDFGV0.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = SDFGV0.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return SDFGV0.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"frames":FieldTypeInfo("I32_V0",I32_V0, True), "flags":FieldTypeInfo("uint32",None, False), "fend":FieldTypeInfo("uint32",None, False), "keys":FieldTypeInfo("FLAGV0",FLAGV0, True)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return SDFGV0.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != SDFGV0:
            raise Exception("%s is not of type %s but %s" % (id, "SDFGV0", type(instance)))
        fieldId = id + ".frames"
        if (type(instance.frames) != list):
            raise Exception("%s is not a list of integers" % (fieldId))
        for itemIndex, item in enumerate(instance.frames):
            itemId = "%s[%d]" % (fieldId, itemIndex)
            if type(item) != int: 
                raise Exception("%s is not an integer" % (itemId))
            if (item < -4294967296) or (item > 4294967295):
                raise Exception("%s has value %d which is not in range [-4294967296, 4294967295]"  % (itemId, item))
        fieldId = id + ".flags"

        if (type(instance.flags) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".fend"

        if (type(instance.fend) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".keys"

        if (type(instance.keys) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "FLAGV0", type(instance.keys)))
        for itemIndex, item in enumerate(instance.keys):
            FLAGV0.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))


class SDMBV0:
    """Animation block with reference to BNDS"""
    fullName = "SDMBV0"
    tagName = "SDMB"
    tagVersion = 0
    size = 32
    structFormat = struct.Struct("<12sII12s")
    fields = ["frames", "flags", "fend", "keys"]

    def __setattr__(self, name, value):
        if name in ["frames", "flags", "fend", "keys"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["frames", "flags", "fend", "keys"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    def resolveReferences(self, sections):
        self.frames = resolveRef(self.frames,sections,I32_V0,"SDMBV0.frames")
        self.keys = resolveRef(self.keys,sections,BNDSV0,"SDMBV0.keys")


    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        if oneOrMore.__class__ == [].__class__:
            for object in oneOrMore:
                object.resolveReferences(sections) 
        else:
            oneOrMore.resolveReferences(sections)

    def introduceIndexReferences(self, indexMaker):
        indexReference = indexMaker.getIndexReferenceTo(self.frames, Reference, I32_V0)
        I32_V0.introduceIndexReferencesForOneOrMore(self.frames,  indexMaker)
        self.frames = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.keys, Reference, BNDSV0)
        BNDSV0.introduceIndexReferencesForOneOrMore(self.keys,  indexMaker)
        self.keys = indexReference


    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        if object.__class__ == MD34IndexEntry:
            return # nothing to do (object was reachable trough 2 paths)
        if object.__class__ == [].__class__:
            for o in object:
                o.introduceIndexReferences(indexMaker) 
        else:
            object.introduceIndexReferences(indexMaker)

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert SDMBV0.size == SDMBV0.structFormat.size
            rawBytes = readable.read(SDMBV0.size)
        if rawBytes != None:
            l = SDMBV0.structFormat.unpack(rawBytes)
            self.frames = Reference(rawBytes=l[0])
            self.flags = l[1]
            self.fend = l[2]
            self.keys = Reference(rawBytes=l[3])
        if (readable == None) and (rawBytes == None):
            self.frames = I32_V0.createEmptyArray()
            self.keys = BNDSV0.createEmptyArray()
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + SDMBV0.size
        for i in range(count):
            list.append(SDMBV0(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += SDMBV0.size
        return list
    
    def toBytes(self):
        return SDMBV0.structFormat.pack(self.frames.toBytes(), self.flags, self.fend, self.keys.toBytes())
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(SDMBV0.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = SDMBV0.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += SDMBV0.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return SDMBV0.countOneOrMore(object) * SDMBV0.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"frames": {}, "fend": {}, "keys": {}, "flags": {}}
    
    def getNamedBit(self, field, bitName):
        mask = SDMBV0.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = SDMBV0.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return SDMBV0.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"frames":FieldTypeInfo("I32_V0",I32_V0, True), "flags":FieldTypeInfo("uint32",None, False), "fend":FieldTypeInfo("uint32",None, False), "keys":FieldTypeInfo("BNDSV0",BNDSV0, True)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return SDMBV0.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != SDMBV0:
            raise Exception("%s is not of type %s but %s" % (id, "SDMBV0", type(instance)))
        fieldId = id + ".frames"
        if (type(instance.frames) != list):
            raise Exception("%s is not a list of integers" % (fieldId))
        for itemIndex, item in enumerate(instance.frames):
            itemId = "%s[%d]" % (fieldId, itemIndex)
            if type(item) != int: 
                raise Exception("%s is not an integer" % (itemId))
            if (item < -4294967296) or (item > 4294967295):
                raise Exception("%s has value %d which is not in range [-4294967296, 4294967295]"  % (itemId, item))
        fieldId = id + ".flags"

        if (type(instance.flags) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".fend"

        if (type(instance.fend) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".keys"

        if (type(instance.keys) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "BNDSV0", type(instance.keys)))
        for itemIndex, item in enumerate(instance.keys):
            BNDSV0.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))


class BONEV1:
    """A bone"""
    fullName = "BONEV1"
    tagName = "BONE"
    tagVersion = 1
    size = 160
    structFormat = struct.Struct("<i12sIhH36s44s36s20s")
    fields = ["d1", "name", "flags", "parent", "s1", "location", "rotation", "scale", "ar1"]

    def __setattr__(self, name, value):
        if name in ["d1", "name", "flags", "parent", "s1", "location", "rotation", "scale", "ar1"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["d1", "name", "flags", "parent", "s1", "location", "rotation", "scale", "ar1"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    def resolveReferences(self, sections):
        self.name = resolveRef(self.name,sections,CHARV0,"BONEV1.name")


    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        if oneOrMore.__class__ == [].__class__:
            for object in oneOrMore:
                object.resolveReferences(sections) 
        else:
            oneOrMore.resolveReferences(sections)

    def introduceIndexReferences(self, indexMaker):
        indexReference = indexMaker.getIndexReferenceTo(self.name, Reference, CHARV0)
        CHARV0.introduceIndexReferencesForOneOrMore(self.name,  indexMaker)
        self.name = indexReference


    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        if object.__class__ == MD34IndexEntry:
            return # nothing to do (object was reachable trough 2 paths)
        if object.__class__ == [].__class__:
            for o in object:
                o.introduceIndexReferences(indexMaker) 
        else:
            object.introduceIndexReferences(indexMaker)

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert BONEV1.size == BONEV1.structFormat.size
            rawBytes = readable.read(BONEV1.size)
        if rawBytes != None:
            l = BONEV1.structFormat.unpack(rawBytes)
            self.d1 = l[0]
            self.name = Reference(rawBytes=l[1])
            self.flags = l[2]
            self.parent = l[3]
            self.s1 = l[4]
            if self.s1 != int(0):
             raise Exception("BONEV1.s1 has value %s instead of the expected value int(0)" % self.s1)
            self.location = Vector3AnimationReference(rawBytes=l[5])
            self.rotation = QuaternionAnimationReference(rawBytes=l[6])
            self.scale = Vector3AnimationReference(rawBytes=l[7])
            self.ar1 = UInt32AnimationReference(rawBytes=l[8])
        if (readable == None) and (rawBytes == None):
            self.d1 = -1
            self.name = CHARV0.createEmptyArray()
            self.flags = 0
            self.parent = -1
            self.s1 = int(0)
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + BONEV1.size
        for i in range(count):
            list.append(BONEV1(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += BONEV1.size
        return list
    
    def toBytes(self):
        return BONEV1.structFormat.pack(self.d1, self.name.toBytes(), self.flags, self.parent, self.s1, self.location.toBytes(), self.rotation.toBytes(), self.scale.toBytes(), self.ar1.toBytes())
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(BONEV1.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = BONEV1.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += BONEV1.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return BONEV1.countOneOrMore(object) * BONEV1.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"ar1": {"real":0x2000, "twoDProjection":0x100, "inverseKinematics ":0x400, "billboard1":0x10, "billboard2":0x40, "inhertTranslation":0x1, "skinned":0x800, "inheritRotation":0x4, "animated":0x200, "inheritScale":0x2}, "scale": {"real":0x2000, "twoDProjection":0x100, "inverseKinematics ":0x400, "billboard1":0x10, "billboard2":0x40, "inhertTranslation":0x1, "skinned":0x800, "inheritRotation":0x4, "animated":0x200, "inheritScale":0x2}, "name": {"real":0x2000, "twoDProjection":0x100, "inverseKinematics ":0x400, "billboard1":0x10, "billboard2":0x40, "inhertTranslation":0x1, "skinned":0x800, "inheritRotation":0x4, "animated":0x200, "inheritScale":0x2}, "parent": {"real":0x2000, "twoDProjection":0x100, "inverseKinematics ":0x400, "billboard1":0x10, "billboard2":0x40, "inhertTranslation":0x1, "skinned":0x800, "inheritRotation":0x4, "animated":0x200, "inheritScale":0x2}, "s1": {"real":0x2000, "twoDProjection":0x100, "inverseKinematics ":0x400, "billboard1":0x10, "billboard2":0x40, "inhertTranslation":0x1, "skinned":0x800, "inheritRotation":0x4, "animated":0x200, "inheritScale":0x2}, "flags": {"real":0x2000, "twoDProjection":0x100, "inverseKinematics ":0x400, "billboard1":0x10, "billboard2":0x40, "inhertTranslation":0x1, "skinned":0x800, "inheritRotation":0x4, "animated":0x200, "inheritScale":0x2}, "location": {"real":0x2000, "twoDProjection":0x100, "inverseKinematics ":0x400, "billboard1":0x10, "billboard2":0x40, "inhertTranslation":0x1, "skinned":0x800, "inheritRotation":0x4, "animated":0x200, "inheritScale":0x2}, "rotation": {"real":0x2000, "twoDProjection":0x100, "inverseKinematics ":0x400, "billboard1":0x10, "billboard2":0x40, "inhertTranslation":0x1, "skinned":0x800, "inheritRotation":0x4, "animated":0x200, "inheritScale":0x2}, "d1": {"real":0x2000, "twoDProjection":0x100, "inverseKinematics ":0x400, "billboard1":0x10, "billboard2":0x40, "inhertTranslation":0x1, "skinned":0x800, "inheritRotation":0x4, "animated":0x200, "inheritScale":0x2}}
    
    def getNamedBit(self, field, bitName):
        mask = BONEV1.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = BONEV1.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return BONEV1.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"d1":FieldTypeInfo("int32",None, False), "name":FieldTypeInfo("CHARV0",CHARV0, True), "flags":FieldTypeInfo("uint32",None, False), "parent":FieldTypeInfo("int16",None, False), "s1":FieldTypeInfo("uint16",None, False), "location":FieldTypeInfo("Vector3AnimationReference",Vector3AnimationReference, False), "rotation":FieldTypeInfo("QuaternionAnimationReference",QuaternionAnimationReference, False), "scale":FieldTypeInfo("Vector3AnimationReference",Vector3AnimationReference, False), "ar1":FieldTypeInfo("UInt32AnimationReference",UInt32AnimationReference, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return BONEV1.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != BONEV1:
            raise Exception("%s is not of type %s but %s" % (id, "BONEV1", type(instance)))
        fieldId = id + ".d1"

        if (type(instance.d1) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".name"

        if (instance.name != None) and (type(instance.name) != str):
            raise Exception("%s is not a string but a %s" % (fieldId, type(instance.name) ))
        fieldId = id + ".flags"

        if (type(instance.flags) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".parent"

        if (type(instance.parent) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".s1"

        if (type(instance.s1) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".location"

        Vector3AnimationReference.validateInstance(instance.location, fieldId)
        fieldId = id + ".rotation"

        QuaternionAnimationReference.validateInstance(instance.rotation, fieldId)
        fieldId = id + ".scale"

        Vector3AnimationReference.validateInstance(instance.scale, fieldId)
        fieldId = id + ".ar1"

        UInt32AnimationReference.validateInstance(instance.ar1, fieldId)


class STC_V4:
    """Sequence Transformations Collection
                animId: array of animation ids
                animref: array of integers is actually an array of short pairs:
                first 2 bytes: index which determines the field in this struct and thus kind
                of the animation data.
                    e.g. 0 -> sdev, 1 -> sd2v etc.
                second: index in animation reference. e.g. sdev[index]
                
                There also seems to be always be the animation id:
                0x65bd3215 which referes to sdev[0] which has a name called "Evt_SeqEnd"
                Strangly it gets from no where referenced and is always the same id
                """
    fullName = "STC_V4"
    tagName = "STC_"
    tagVersion = 4
    size = 204
    structFormat = struct.Struct("<12sIHH12s12sI12s12s12s12s12s12s12s12s12s12s12s12s12s")
    fields = ["name", "d1", "seqIndex", "stgIndex", "animIds", "animRefs", "d2", "sdev", "sd2v", "sd3v", "sd4q", "sdcc", "sdr3", "unknownRef8", "sds6", "sdu6", "unknownRef11", "unknownRef12", "sdfg", "sdmb"]

    def __setattr__(self, name, value):
        if name in ["name", "d1", "seqIndex", "stgIndex", "animIds", "animRefs", "d2", "sdev", "sd2v", "sd3v", "sd4q", "sdcc", "sdr3", "unknownRef8", "sds6", "sdu6", "unknownRef11", "unknownRef12", "sdfg", "sdmb"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["name", "d1", "seqIndex", "stgIndex", "animIds", "animRefs", "d2", "sdev", "sd2v", "sd3v", "sd4q", "sdcc", "sdr3", "unknownRef8", "sds6", "sdu6", "unknownRef11", "unknownRef12", "sdfg", "sdmb"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    def resolveReferences(self, sections):
        self.name = resolveRef(self.name,sections,CHARV0,"STC_V4.name")
        self.animIds = resolveRef(self.animIds,sections,U32_V0,"STC_V4.animIds")
        self.animRefs = resolveRef(self.animRefs,sections,U32_V0,"STC_V4.animRefs")
        self.sdev = resolveRef(self.sdev,sections,SDEVV0,"STC_V4.sdev")
        self.sd2v = resolveRef(self.sd2v,sections,SD2VV0,"STC_V4.sd2v")
        self.sd3v = resolveRef(self.sd3v,sections,SD3VV0,"STC_V4.sd3v")
        self.sd4q = resolveRef(self.sd4q,sections,SD4QV0,"STC_V4.sd4q")
        self.sdcc = resolveRef(self.sdcc,sections,SDCCV0,"STC_V4.sdcc")
        self.sdr3 = resolveRef(self.sdr3,sections,SDR3V0,"STC_V4.sdr3")
        self.unknownRef8 = resolveRef(self.unknownRef8,sections,None,"STC_V4.unknownRef8")
        self.sds6 = resolveRef(self.sds6,sections,SDS6V0,"STC_V4.sds6")
        self.sdu6 = resolveRef(self.sdu6,sections,SDU6V0,"STC_V4.sdu6")
        self.unknownRef11 = resolveRef(self.unknownRef11,sections,None,"STC_V4.unknownRef11")
        self.unknownRef12 = resolveRef(self.unknownRef12,sections,None,"STC_V4.unknownRef12")
        self.sdfg = resolveRef(self.sdfg,sections,SDFGV0,"STC_V4.sdfg")
        self.sdmb = resolveRef(self.sdmb,sections,SDMBV0,"STC_V4.sdmb")


    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        if oneOrMore.__class__ == [].__class__:
            for object in oneOrMore:
                object.resolveReferences(sections) 
        else:
            oneOrMore.resolveReferences(sections)

    def introduceIndexReferences(self, indexMaker):
        indexReference = indexMaker.getIndexReferenceTo(self.name, Reference, CHARV0)
        CHARV0.introduceIndexReferencesForOneOrMore(self.name,  indexMaker)
        self.name = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.animIds, Reference, U32_V0)
        U32_V0.introduceIndexReferencesForOneOrMore(self.animIds,  indexMaker)
        self.animIds = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.animRefs, Reference, U32_V0)
        U32_V0.introduceIndexReferencesForOneOrMore(self.animRefs,  indexMaker)
        self.animRefs = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.sdev, Reference, SDEVV0)
        SDEVV0.introduceIndexReferencesForOneOrMore(self.sdev,  indexMaker)
        self.sdev = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.sd2v, Reference, SD2VV0)
        SD2VV0.introduceIndexReferencesForOneOrMore(self.sd2v,  indexMaker)
        self.sd2v = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.sd3v, Reference, SD3VV0)
        SD3VV0.introduceIndexReferencesForOneOrMore(self.sd3v,  indexMaker)
        self.sd3v = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.sd4q, Reference, SD4QV0)
        SD4QV0.introduceIndexReferencesForOneOrMore(self.sd4q,  indexMaker)
        self.sd4q = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.sdcc, Reference, SDCCV0)
        SDCCV0.introduceIndexReferencesForOneOrMore(self.sdcc,  indexMaker)
        self.sdcc = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.sdr3, Reference, SDR3V0)
        SDR3V0.introduceIndexReferencesForOneOrMore(self.sdr3,  indexMaker)
        self.sdr3 = indexReference
        self.unknownRef8 = indexMaker.getIndexReferenceTo(self.unknownRef8, Reference, None)
        indexReference = indexMaker.getIndexReferenceTo(self.sds6, Reference, SDS6V0)
        SDS6V0.introduceIndexReferencesForOneOrMore(self.sds6,  indexMaker)
        self.sds6 = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.sdu6, Reference, SDU6V0)
        SDU6V0.introduceIndexReferencesForOneOrMore(self.sdu6,  indexMaker)
        self.sdu6 = indexReference
        self.unknownRef11 = indexMaker.getIndexReferenceTo(self.unknownRef11, Reference, None)
        self.unknownRef12 = indexMaker.getIndexReferenceTo(self.unknownRef12, Reference, None)
        indexReference = indexMaker.getIndexReferenceTo(self.sdfg, Reference, SDFGV0)
        SDFGV0.introduceIndexReferencesForOneOrMore(self.sdfg,  indexMaker)
        self.sdfg = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.sdmb, Reference, SDMBV0)
        SDMBV0.introduceIndexReferencesForOneOrMore(self.sdmb,  indexMaker)
        self.sdmb = indexReference


    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        if object.__class__ == MD34IndexEntry:
            return # nothing to do (object was reachable trough 2 paths)
        if object.__class__ == [].__class__:
            for o in object:
                o.introduceIndexReferences(indexMaker) 
        else:
            object.introduceIndexReferences(indexMaker)

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert STC_V4.size == STC_V4.structFormat.size
            rawBytes = readable.read(STC_V4.size)
        if rawBytes != None:
            l = STC_V4.structFormat.unpack(rawBytes)
            self.name = Reference(rawBytes=l[0])
            self.d1 = l[1]
            self.seqIndex = l[2]
            self.stgIndex = l[3]
            self.animIds = Reference(rawBytes=l[4])
            self.animRefs = Reference(rawBytes=l[5])
            self.d2 = l[6]
            if self.d2 != int(0):
             raise Exception("STC_V4.d2 has value %s instead of the expected value int(0)" % self.d2)
            self.sdev = Reference(rawBytes=l[7])
            self.sd2v = Reference(rawBytes=l[8])
            self.sd3v = Reference(rawBytes=l[9])
            self.sd4q = Reference(rawBytes=l[10])
            self.sdcc = Reference(rawBytes=l[11])
            self.sdr3 = Reference(rawBytes=l[12])
            self.unknownRef8 = Reference(rawBytes=l[13])
            self.sds6 = Reference(rawBytes=l[14])
            self.sdu6 = Reference(rawBytes=l[15])
            self.unknownRef11 = Reference(rawBytes=l[16])
            self.unknownRef12 = Reference(rawBytes=l[17])
            self.sdfg = Reference(rawBytes=l[18])
            self.sdmb = Reference(rawBytes=l[19])
        if (readable == None) and (rawBytes == None):
            self.name = CHARV0.createEmptyArray()
            self.d1 = 0
            self.animIds = U32_V0.createEmptyArray()
            self.animRefs = U32_V0.createEmptyArray()
            self.d2 = int(0)
            self.sdev = SDEVV0.createEmptyArray()
            self.sd2v = SD2VV0.createEmptyArray()
            self.sd3v = SD3VV0.createEmptyArray()
            self.sd4q = SD4QV0.createEmptyArray()
            self.sdcc = SDCCV0.createEmptyArray()
            self.sdr3 = SDR3V0.createEmptyArray()
            self.unknownRef8 = []
            self.sds6 = SDS6V0.createEmptyArray()
            self.sdu6 = SDU6V0.createEmptyArray()
            self.unknownRef11 = []
            self.unknownRef12 = []
            self.sdfg = SDFGV0.createEmptyArray()
            self.sdmb = SDMBV0.createEmptyArray()
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + STC_V4.size
        for i in range(count):
            list.append(STC_V4(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += STC_V4.size
        return list
    
    def toBytes(self):
        return STC_V4.structFormat.pack(self.name.toBytes(), self.d1, self.seqIndex, self.stgIndex, self.animIds.toBytes(), self.animRefs.toBytes(), self.d2, self.sdev.toBytes(), self.sd2v.toBytes(), self.sd3v.toBytes(), self.sd4q.toBytes(), self.sdcc.toBytes(), self.sdr3.toBytes(), self.unknownRef8.toBytes(), self.sds6.toBytes(), self.sdu6.toBytes(), self.unknownRef11.toBytes(), self.unknownRef12.toBytes(), self.sdfg.toBytes(), self.sdmb.toBytes())
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(STC_V4.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = STC_V4.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += STC_V4.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return STC_V4.countOneOrMore(object) * STC_V4.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"sdfg": {}, "animIds": {}, "name": {}, "unknownRef12": {}, "sd4q": {}, "unknownRef11": {}, "stgIndex": {}, "sdev": {}, "seqIndex": {}, "unknownRef8": {}, "sdmb": {}, "sdu6": {}, "sds6": {}, "sdr3": {}, "animRefs": {}, "sdcc": {}, "d2": {}, "sd2v": {}, "sd3v": {}, "d1": {}}
    
    def getNamedBit(self, field, bitName):
        mask = STC_V4.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = STC_V4.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return STC_V4.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"name":FieldTypeInfo("CHARV0",CHARV0, True), "d1":FieldTypeInfo("uint32",None, False), "seqIndex":FieldTypeInfo("uint16",None, False), "stgIndex":FieldTypeInfo("uint16",None, False), "animIds":FieldTypeInfo("U32_V0",U32_V0, True), "animRefs":FieldTypeInfo("U32_V0",U32_V0, True), "d2":FieldTypeInfo("uint32",None, False), "sdev":FieldTypeInfo("SDEVV0",SDEVV0, True), "sd2v":FieldTypeInfo("SD2VV0",SD2VV0, True), "sd3v":FieldTypeInfo("SD3VV0",SD3VV0, True), "sd4q":FieldTypeInfo("SD4QV0",SD4QV0, True), "sdcc":FieldTypeInfo("SDCCV0",SDCCV0, True), "sdr3":FieldTypeInfo("SDR3V0",SDR3V0, True), "unknownRef8":FieldTypeInfo(None,None, True), "sds6":FieldTypeInfo("SDS6V0",SDS6V0, True), "sdu6":FieldTypeInfo("SDU6V0",SDU6V0, True), "unknownRef11":FieldTypeInfo(None,None, True), "unknownRef12":FieldTypeInfo(None,None, True), "sdfg":FieldTypeInfo("SDFGV0",SDFGV0, True), "sdmb":FieldTypeInfo("SDMBV0",SDMBV0, True)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return STC_V4.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != STC_V4:
            raise Exception("%s is not of type %s but %s" % (id, "STC_V4", type(instance)))
        fieldId = id + ".name"

        if (instance.name != None) and (type(instance.name) != str):
            raise Exception("%s is not a string but a %s" % (fieldId, type(instance.name) ))
        fieldId = id + ".d1"

        if (type(instance.d1) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".seqIndex"

        if (type(instance.seqIndex) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".stgIndex"

        if (type(instance.stgIndex) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".animIds"
        if (type(instance.animIds) != list):
            raise Exception("%s is not a list of integers" % (fieldId))
        for itemIndex, item in enumerate(instance.animIds):
            itemId = "%s[%d]" % (fieldId, itemIndex)
            if type(item) != int: 
                raise Exception("%s is not an integer" % (itemId))
            if (item < 0) or (item > 8589934591):
                raise Exception("%s has value %d which is not in range [0, 8589934591]"  % (itemId, item))
        fieldId = id + ".animRefs"
        if (type(instance.animRefs) != list):
            raise Exception("%s is not a list of integers" % (fieldId))
        for itemIndex, item in enumerate(instance.animRefs):
            itemId = "%s[%d]" % (fieldId, itemIndex)
            if type(item) != int: 
                raise Exception("%s is not an integer" % (itemId))
            if (item < 0) or (item > 8589934591):
                raise Exception("%s has value %d which is not in range [0, 8589934591]"  % (itemId, item))
        fieldId = id + ".d2"

        if (type(instance.d2) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".sdev"

        if (type(instance.sdev) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "SDEVV0", type(instance.sdev)))
        for itemIndex, item in enumerate(instance.sdev):
            SDEVV0.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".sd2v"

        if (type(instance.sd2v) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "SD2VV0", type(instance.sd2v)))
        for itemIndex, item in enumerate(instance.sd2v):
            SD2VV0.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".sd3v"

        if (type(instance.sd3v) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "SD3VV0", type(instance.sd3v)))
        for itemIndex, item in enumerate(instance.sd3v):
            SD3VV0.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".sd4q"

        if (type(instance.sd4q) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "SD4QV0", type(instance.sd4q)))
        for itemIndex, item in enumerate(instance.sd4q):
            SD4QV0.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".sdcc"

        if (type(instance.sdcc) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "SDCCV0", type(instance.sdcc)))
        for itemIndex, item in enumerate(instance.sdcc):
            SDCCV0.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".sdr3"

        if (type(instance.sdr3) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "SDR3V0", type(instance.sdr3)))
        for itemIndex, item in enumerate(instance.sdr3):
            SDR3V0.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".unknownRef8"

        if (type(instance.unknownRef8) != list) or (len(instance.unknownRef8) != 0):
            raise Exception("%s is not an empty list" % (fieldId))
        fieldId = id + ".sds6"

        if (type(instance.sds6) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "SDS6V0", type(instance.sds6)))
        for itemIndex, item in enumerate(instance.sds6):
            SDS6V0.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".sdu6"

        if (type(instance.sdu6) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "SDU6V0", type(instance.sdu6)))
        for itemIndex, item in enumerate(instance.sdu6):
            SDU6V0.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".unknownRef11"

        if (type(instance.unknownRef11) != list) or (len(instance.unknownRef11) != 0):
            raise Exception("%s is not an empty list" % (fieldId))
        fieldId = id + ".unknownRef12"

        if (type(instance.unknownRef12) != list) or (len(instance.unknownRef12) != 0):
            raise Exception("%s is not an empty list" % (fieldId))
        fieldId = id + ".sdfg"

        if (type(instance.sdfg) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "SDFGV0", type(instance.sdfg)))
        for itemIndex, item in enumerate(instance.sdfg):
            SDFGV0.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".sdmb"

        if (type(instance.sdmb) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "SDMBV0", type(instance.sdmb)))
        for itemIndex, item in enumerate(instance.sdmb):
            SDMBV0.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))


class SEQSV1:
    """Animation Sequence"""
    fullName = "SEQSV1"
    tagName = "SEQS"
    tagVersion = 1
    size = 96
    structFormat = struct.Struct("<ii12sIIfIIIIII28sIII")
    fields = ["unknown0", "unknown1", "name", "animStartInMS", "animEndInMS", "movementSpeed", "flags", "frequency", "unknown2", "unknown3", "unknown4", "unknown5", "boundingSphere", "unknown6", "unknown7", "unknown8"]

    def __setattr__(self, name, value):
        if name in ["unknown0", "unknown1", "name", "animStartInMS", "animEndInMS", "movementSpeed", "flags", "frequency", "unknown2", "unknown3", "unknown4", "unknown5", "boundingSphere", "unknown6", "unknown7", "unknown8"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["unknown0", "unknown1", "name", "animStartInMS", "animEndInMS", "movementSpeed", "flags", "frequency", "unknown2", "unknown3", "unknown4", "unknown5", "boundingSphere", "unknown6", "unknown7", "unknown8"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    def resolveReferences(self, sections):
        self.name = resolveRef(self.name,sections,CHARV0,"SEQSV1.name")


    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        if oneOrMore.__class__ == [].__class__:
            for object in oneOrMore:
                object.resolveReferences(sections) 
        else:
            oneOrMore.resolveReferences(sections)

    def introduceIndexReferences(self, indexMaker):
        indexReference = indexMaker.getIndexReferenceTo(self.name, Reference, CHARV0)
        CHARV0.introduceIndexReferencesForOneOrMore(self.name,  indexMaker)
        self.name = indexReference


    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        if object.__class__ == MD34IndexEntry:
            return # nothing to do (object was reachable trough 2 paths)
        if object.__class__ == [].__class__:
            for o in object:
                o.introduceIndexReferences(indexMaker) 
        else:
            object.introduceIndexReferences(indexMaker)

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert SEQSV1.size == SEQSV1.structFormat.size
            rawBytes = readable.read(SEQSV1.size)
        if rawBytes != None:
            l = SEQSV1.structFormat.unpack(rawBytes)
            self.unknown0 = l[0]
            self.unknown1 = l[1]
            self.name = Reference(rawBytes=l[2])
            self.animStartInMS = l[3]
            self.animEndInMS = l[4]
            self.movementSpeed = l[5]
            self.flags = l[6]
            self.frequency = l[7]
            self.unknown2 = l[8]
            if self.unknown2 != int(1):
             raise Exception("SEQSV1.unknown2 has value %s instead of the expected value int(1)" % self.unknown2)
            self.unknown3 = l[9]
            if self.unknown3 != int(1):
             raise Exception("SEQSV1.unknown3 has value %s instead of the expected value int(1)" % self.unknown3)
            self.unknown4 = l[10]
            if self.unknown4 != int(100):
             raise Exception("SEQSV1.unknown4 has value %s instead of the expected value int(100)" % self.unknown4)
            self.unknown5 = l[11]
            if self.unknown5 != int(0):
             raise Exception("SEQSV1.unknown5 has value %s instead of the expected value int(0)" % self.unknown5)
            self.boundingSphere = BNDSV0(rawBytes=l[12])
            self.unknown6 = l[13]
            if self.unknown6 != int(0):
             raise Exception("SEQSV1.unknown6 has value %s instead of the expected value int(0)" % self.unknown6)
            self.unknown7 = l[14]
            if self.unknown7 != int(0):
             raise Exception("SEQSV1.unknown7 has value %s instead of the expected value int(0)" % self.unknown7)
            self.unknown8 = l[15]
            if self.unknown8 != int(0):
             raise Exception("SEQSV1.unknown8 has value %s instead of the expected value int(0)" % self.unknown8)
        if (readable == None) and (rawBytes == None):
            self.unknown0 = -1
            self.unknown1 = -1
            self.name = CHARV0.createEmptyArray()
            self.flags = 0
            self.unknown2 = int(1)
            self.unknown3 = int(1)
            self.unknown4 = int(100)
            self.unknown5 = int(0)
            self.unknown6 = int(0)
            self.unknown7 = int(0)
            self.unknown8 = int(0)
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + SEQSV1.size
        for i in range(count):
            list.append(SEQSV1(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += SEQSV1.size
        return list
    
    def toBytes(self):
        return SEQSV1.structFormat.pack(self.unknown0, self.unknown1, self.name.toBytes(), self.animStartInMS, self.animEndInMS, self.movementSpeed, self.flags, self.frequency, self.unknown2, self.unknown3, self.unknown4, self.unknown5, self.boundingSphere.toBytes(), self.unknown6, self.unknown7, self.unknown8)
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(SEQSV1.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = SEQSV1.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += SEQSV1.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return SEQSV1.countOneOrMore(object) * SEQSV1.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"animEndInMS": {"notLooping":0x1, "globalInPreviewer":0x8, "alwaysGlobal":0x2}, "name": {"notLooping":0x1, "globalInPreviewer":0x8, "alwaysGlobal":0x2}, "boundingSphere": {"notLooping":0x1, "globalInPreviewer":0x8, "alwaysGlobal":0x2}, "frequency": {"notLooping":0x1, "globalInPreviewer":0x8, "alwaysGlobal":0x2}, "unknown2": {"notLooping":0x1, "globalInPreviewer":0x8, "alwaysGlobal":0x2}, "unknown3": {"notLooping":0x1, "globalInPreviewer":0x8, "alwaysGlobal":0x2}, "unknown0": {"notLooping":0x1, "globalInPreviewer":0x8, "alwaysGlobal":0x2}, "unknown1": {"notLooping":0x1, "globalInPreviewer":0x8, "alwaysGlobal":0x2}, "flags": {"notLooping":0x1, "globalInPreviewer":0x8, "alwaysGlobal":0x2}, "unknown7": {"notLooping":0x1, "globalInPreviewer":0x8, "alwaysGlobal":0x2}, "unknown4": {"notLooping":0x1, "globalInPreviewer":0x8, "alwaysGlobal":0x2}, "unknown5": {"notLooping":0x1, "globalInPreviewer":0x8, "alwaysGlobal":0x2}, "unknown6": {"notLooping":0x1, "globalInPreviewer":0x8, "alwaysGlobal":0x2}, "unknown8": {"notLooping":0x1, "globalInPreviewer":0x8, "alwaysGlobal":0x2}, "movementSpeed": {"notLooping":0x1, "globalInPreviewer":0x8, "alwaysGlobal":0x2}, "animStartInMS": {"notLooping":0x1, "globalInPreviewer":0x8, "alwaysGlobal":0x2}}
    
    def getNamedBit(self, field, bitName):
        mask = SEQSV1.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = SEQSV1.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return SEQSV1.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"unknown0":FieldTypeInfo("int32",None, False), "unknown1":FieldTypeInfo("int32",None, False), "name":FieldTypeInfo("CHARV0",CHARV0, True), "animStartInMS":FieldTypeInfo("uint32",None, False), "animEndInMS":FieldTypeInfo("uint32",None, False), "movementSpeed":FieldTypeInfo("float",None, False), "flags":FieldTypeInfo("uint32",None, False), "frequency":FieldTypeInfo("uint32",None, False), "unknown2":FieldTypeInfo("uint32",None, False), "unknown3":FieldTypeInfo("uint32",None, False), "unknown4":FieldTypeInfo("uint32",None, False), "unknown5":FieldTypeInfo("uint32",None, False), "boundingSphere":FieldTypeInfo("BNDSV0",BNDSV0, False), "unknown6":FieldTypeInfo("uint32",None, False), "unknown7":FieldTypeInfo("uint32",None, False), "unknown8":FieldTypeInfo("uint32",None, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return SEQSV1.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != SEQSV1:
            raise Exception("%s is not of type %s but %s" % (id, "SEQSV1", type(instance)))
        fieldId = id + ".unknown0"

        if (type(instance.unknown0) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".unknown1"

        if (type(instance.unknown1) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".name"

        if (instance.name != None) and (type(instance.name) != str):
            raise Exception("%s is not a string but a %s" % (fieldId, type(instance.name) ))
        fieldId = id + ".animStartInMS"

        if (type(instance.animStartInMS) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".animEndInMS"

        if (type(instance.animEndInMS) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".movementSpeed"

        if (type(instance.movementSpeed) != float):
            raise Exception("%s is not a float" % (fieldId))
        fieldId = id + ".flags"

        if (type(instance.flags) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".frequency"

        if (type(instance.frequency) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".unknown2"

        if (type(instance.unknown2) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".unknown3"

        if (type(instance.unknown3) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".unknown4"

        if (type(instance.unknown4) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".unknown5"

        if (type(instance.unknown5) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".boundingSphere"

        BNDSV0.validateInstance(instance.boundingSphere, fieldId)
        fieldId = id + ".unknown6"

        if (type(instance.unknown6) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".unknown7"

        if (type(instance.unknown7) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".unknown8"

        if (type(instance.unknown8) != int):
            raise Exception("%s is not an int" % (fieldId))


class STG_V0:
    """
                Seqeuence Transformation Group which can contain multiple STCs
                referenced by index as they are listed in the model.
                """
    fullName = "STG_V0"
    tagName = "STG_"
    tagVersion = 0
    size = 24
    structFormat = struct.Struct("<12s12s")
    fields = ["name", "stcIndices"]

    def __setattr__(self, name, value):
        if name in ["name", "stcIndices"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["name", "stcIndices"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    def resolveReferences(self, sections):
        self.name = resolveRef(self.name,sections,CHARV0,"STG_V0.name")
        self.stcIndices = resolveRef(self.stcIndices,sections,U32_V0,"STG_V0.stcIndices")


    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        if oneOrMore.__class__ == [].__class__:
            for object in oneOrMore:
                object.resolveReferences(sections) 
        else:
            oneOrMore.resolveReferences(sections)

    def introduceIndexReferences(self, indexMaker):
        indexReference = indexMaker.getIndexReferenceTo(self.name, Reference, CHARV0)
        CHARV0.introduceIndexReferencesForOneOrMore(self.name,  indexMaker)
        self.name = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.stcIndices, Reference, U32_V0)
        U32_V0.introduceIndexReferencesForOneOrMore(self.stcIndices,  indexMaker)
        self.stcIndices = indexReference


    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        if object.__class__ == MD34IndexEntry:
            return # nothing to do (object was reachable trough 2 paths)
        if object.__class__ == [].__class__:
            for o in object:
                o.introduceIndexReferences(indexMaker) 
        else:
            object.introduceIndexReferences(indexMaker)

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert STG_V0.size == STG_V0.structFormat.size
            rawBytes = readable.read(STG_V0.size)
        if rawBytes != None:
            l = STG_V0.structFormat.unpack(rawBytes)
            self.name = Reference(rawBytes=l[0])
            self.stcIndices = Reference(rawBytes=l[1])
        if (readable == None) and (rawBytes == None):
            self.name = CHARV0.createEmptyArray()
            self.stcIndices = U32_V0.createEmptyArray()
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + STG_V0.size
        for i in range(count):
            list.append(STG_V0(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += STG_V0.size
        return list
    
    def toBytes(self):
        return STG_V0.structFormat.pack(self.name.toBytes(), self.stcIndices.toBytes())
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(STG_V0.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = STG_V0.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += STG_V0.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return STG_V0.countOneOrMore(object) * STG_V0.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"stcIndices": {}, "name": {}}
    
    def getNamedBit(self, field, bitName):
        mask = STG_V0.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = STG_V0.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return STG_V0.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"name":FieldTypeInfo("CHARV0",CHARV0, True), "stcIndices":FieldTypeInfo("U32_V0",U32_V0, True)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return STG_V0.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != STG_V0:
            raise Exception("%s is not of type %s but %s" % (id, "STG_V0", type(instance)))
        fieldId = id + ".name"

        if (instance.name != None) and (type(instance.name) != str):
            raise Exception("%s is not a string but a %s" % (fieldId, type(instance.name) ))
        fieldId = id + ".stcIndices"
        if (type(instance.stcIndices) != list):
            raise Exception("%s is not a list of integers" % (fieldId))
        for itemIndex, item in enumerate(instance.stcIndices):
            itemId = "%s[%d]" % (fieldId, itemIndex)
            if type(item) != int: 
                raise Exception("%s is not an integer" % (itemId))
            if (item < 0) or (item > 8589934591):
                raise Exception("%s has value %d which is not in range [0, 8589934591]"  % (itemId, item))


class STS_V0:
    """"""
    fullName = "STS_V0"
    tagName = "STS_"
    tagVersion = 0
    size = 28
    structFormat = struct.Struct("<12siiihH")
    fields = ["animIds", "unknown0", "unknown1", "unknown2", "s1", "s2"]

    def __setattr__(self, name, value):
        if name in ["animIds", "unknown0", "unknown1", "unknown2", "s1", "s2"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["animIds", "unknown0", "unknown1", "unknown2", "s1", "s2"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    def resolveReferences(self, sections):
        self.animIds = resolveRef(self.animIds,sections,U32_V0,"STS_V0.animIds")


    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        if oneOrMore.__class__ == [].__class__:
            for object in oneOrMore:
                object.resolveReferences(sections) 
        else:
            oneOrMore.resolveReferences(sections)

    def introduceIndexReferences(self, indexMaker):
        indexReference = indexMaker.getIndexReferenceTo(self.animIds, Reference, U32_V0)
        U32_V0.introduceIndexReferencesForOneOrMore(self.animIds,  indexMaker)
        self.animIds = indexReference


    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        if object.__class__ == MD34IndexEntry:
            return # nothing to do (object was reachable trough 2 paths)
        if object.__class__ == [].__class__:
            for o in object:
                o.introduceIndexReferences(indexMaker) 
        else:
            object.introduceIndexReferences(indexMaker)

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert STS_V0.size == STS_V0.structFormat.size
            rawBytes = readable.read(STS_V0.size)
        if rawBytes != None:
            l = STS_V0.structFormat.unpack(rawBytes)
            self.animIds = Reference(rawBytes=l[0])
            self.unknown0 = l[1]
            if self.unknown0 != int(-1):
             raise Exception("STS_V0.unknown0 has value %s instead of the expected value int(-1)" % self.unknown0)
            self.unknown1 = l[2]
            if self.unknown1 != int(-1):
             raise Exception("STS_V0.unknown1 has value %s instead of the expected value int(-1)" % self.unknown1)
            self.unknown2 = l[3]
            if self.unknown2 != int(-1):
             raise Exception("STS_V0.unknown2 has value %s instead of the expected value int(-1)" % self.unknown2)
            self.s1 = l[4]
            if self.s1 != int(-1):
             raise Exception("STS_V0.s1 has value %s instead of the expected value int(-1)" % self.s1)
            self.s2 = l[5]
            if self.s2 != int(0):
             raise Exception("STS_V0.s2 has value %s instead of the expected value int(0)" % self.s2)
        if (readable == None) and (rawBytes == None):
            self.animIds = U32_V0.createEmptyArray()
            self.unknown0 = int(-1)
            self.unknown1 = int(-1)
            self.unknown2 = int(-1)
            self.s1 = int(-1)
            self.s2 = int(0)
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + STS_V0.size
        for i in range(count):
            list.append(STS_V0(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += STS_V0.size
        return list
    
    def toBytes(self):
        return STS_V0.structFormat.pack(self.animIds.toBytes(), self.unknown0, self.unknown1, self.unknown2, self.s1, self.s2)
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(STS_V0.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = STS_V0.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += STS_V0.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return STS_V0.countOneOrMore(object) * STS_V0.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"animIds": {}, "s2": {}, "s1": {}, "unknown2": {}, "unknown0": {}, "unknown1": {}}
    
    def getNamedBit(self, field, bitName):
        mask = STS_V0.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = STS_V0.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return STS_V0.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"animIds":FieldTypeInfo("U32_V0",U32_V0, True), "unknown0":FieldTypeInfo("int32",None, False), "unknown1":FieldTypeInfo("int32",None, False), "unknown2":FieldTypeInfo("int32",None, False), "s1":FieldTypeInfo("int16",None, False), "s2":FieldTypeInfo("uint16",None, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return STS_V0.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != STS_V0:
            raise Exception("%s is not of type %s but %s" % (id, "STS_V0", type(instance)))
        fieldId = id + ".animIds"
        if (type(instance.animIds) != list):
            raise Exception("%s is not a list of integers" % (fieldId))
        for itemIndex, item in enumerate(instance.animIds):
            itemId = "%s[%d]" % (fieldId, itemIndex)
            if type(item) != int: 
                raise Exception("%s is not an integer" % (itemId))
            if (item < 0) or (item > 8589934591):
                raise Exception("%s has value %d which is not in range [0, 8589934591]"  % (itemId, item))
        fieldId = id + ".unknown0"

        if (type(instance.unknown0) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".unknown1"

        if (type(instance.unknown1) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".unknown2"

        if (type(instance.unknown2) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".s1"

        if (type(instance.s1) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".s2"

        if (type(instance.s2) != int):
            raise Exception("%s is not an int" % (fieldId))


class IREFV0:
    """Just a 4x4 matrix"""
    fullName = "IREFV0"
    tagName = "IREF"
    tagVersion = 0
    size = 64
    structFormat = struct.Struct("<64s")
    fields = ["matrix"]

    def __setattr__(self, name, value):
        if name in ["matrix"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["matrix"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        pass #nothing to do
    
    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        pass #nothing to do

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert IREFV0.size == IREFV0.structFormat.size
            rawBytes = readable.read(IREFV0.size)
        if rawBytes != None:
            l = IREFV0.structFormat.unpack(rawBytes)
            self.matrix = Matrix44(rawBytes=l[0])
        if (readable == None) and (rawBytes == None):
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + IREFV0.size
        for i in range(count):
            list.append(IREFV0(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += IREFV0.size
        return list
    
    def toBytes(self):
        return IREFV0.structFormat.pack(self.matrix.toBytes())
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(IREFV0.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = IREFV0.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += IREFV0.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return IREFV0.countOneOrMore(object) * IREFV0.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"matrix": {}}
    
    def getNamedBit(self, field, bitName):
        mask = IREFV0.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = IREFV0.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return IREFV0.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"matrix":FieldTypeInfo("Matrix44",Matrix44, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return IREFV0.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != IREFV0:
            raise Exception("%s is not of type %s but %s" % (id, "IREFV0", type(instance)))
        fieldId = id + ".matrix"

        Matrix44.validateInstance(instance.matrix, fieldId)


class REGNV3:
    """a kind of submesh"""
    fullName = "REGNV3"
    tagName = "REGN"
    tagVersion = 3
    size = 36
    structFormat = struct.Struct("<IIIIIIHHHHBBH")
    fields = ["unknown0", "unknown1", "firstVertexIndex", "numberOfVertices", "firstFaceVertexIndexIndex", "numberOfFaceVertexIndices", "numberOfBones", "firstBoneLookupIndex", "numberOfBoneLookupIndices", "unknown2", "unknown3", "unknown4", "rootBoneIndex"]

    def __setattr__(self, name, value):
        if name in ["unknown0", "unknown1", "firstVertexIndex", "numberOfVertices", "firstFaceVertexIndexIndex", "numberOfFaceVertexIndices", "numberOfBones", "firstBoneLookupIndex", "numberOfBoneLookupIndices", "unknown2", "unknown3", "unknown4", "rootBoneIndex"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["unknown0", "unknown1", "firstVertexIndex", "numberOfVertices", "firstFaceVertexIndexIndex", "numberOfFaceVertexIndices", "numberOfBones", "firstBoneLookupIndex", "numberOfBoneLookupIndices", "unknown2", "unknown3", "unknown4", "rootBoneIndex"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        pass #nothing to do
    
    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        pass #nothing to do

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert REGNV3.size == REGNV3.structFormat.size
            rawBytes = readable.read(REGNV3.size)
        if rawBytes != None:
            l = REGNV3.structFormat.unpack(rawBytes)
            self.unknown0 = l[0]
            if self.unknown0 != int(0):
             raise Exception("REGNV3.unknown0 has value %s instead of the expected value int(0)" % self.unknown0)
            self.unknown1 = l[1]
            if self.unknown1 != int(0):
             raise Exception("REGNV3.unknown1 has value %s instead of the expected value int(0)" % self.unknown1)
            self.firstVertexIndex = l[2]
            self.numberOfVertices = l[3]
            self.firstFaceVertexIndexIndex = l[4]
            self.numberOfFaceVertexIndices = l[5]
            self.numberOfBones = l[6]
            self.firstBoneLookupIndex = l[7]
            self.numberOfBoneLookupIndices = l[8]
            self.unknown2 = l[9]
            if self.unknown2 != int(0):
             raise Exception("REGNV3.unknown2 has value %s instead of the expected value int(0)" % self.unknown2)
            self.unknown3 = l[10]
            self.unknown4 = l[11]
            self.rootBoneIndex = l[12]
        if (readable == None) and (rawBytes == None):
            self.unknown0 = int(0)
            self.unknown1 = int(0)
            self.unknown2 = int(0)
            self.unknown3 = 1
            self.unknown4 = 1
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + REGNV3.size
        for i in range(count):
            list.append(REGNV3(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += REGNV3.size
        return list
    
    def toBytes(self):
        return REGNV3.structFormat.pack(self.unknown0, self.unknown1, self.firstVertexIndex, self.numberOfVertices, self.firstFaceVertexIndexIndex, self.numberOfFaceVertexIndices, self.numberOfBones, self.firstBoneLookupIndex, self.numberOfBoneLookupIndices, self.unknown2, self.unknown3, self.unknown4, self.rootBoneIndex)
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(REGNV3.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = REGNV3.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += REGNV3.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return REGNV3.countOneOrMore(object) * REGNV3.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"firstBoneLookupIndex": {}, "rootBoneIndex": {}, "unknown3": {}, "firstVertexIndex": {}, "numberOfBoneLookupIndices": {}, "unknown2": {}, "numberOfVertices": {}, "unknown0": {}, "unknown1": {}, "numberOfBones": {}, "numberOfFaceVertexIndices": {}, "unknown4": {}, "firstFaceVertexIndexIndex": {}}
    
    def getNamedBit(self, field, bitName):
        mask = REGNV3.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = REGNV3.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return REGNV3.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"unknown0":FieldTypeInfo("uint32",None, False), "unknown1":FieldTypeInfo("uint32",None, False), "firstVertexIndex":FieldTypeInfo("uint32",None, False), "numberOfVertices":FieldTypeInfo("uint32",None, False), "firstFaceVertexIndexIndex":FieldTypeInfo("uint32",None, False), "numberOfFaceVertexIndices":FieldTypeInfo("uint32",None, False), "numberOfBones":FieldTypeInfo("uint16",None, False), "firstBoneLookupIndex":FieldTypeInfo("uint16",None, False), "numberOfBoneLookupIndices":FieldTypeInfo("uint16",None, False), "unknown2":FieldTypeInfo("uint16",None, False), "unknown3":FieldTypeInfo("uint8",None, False), "unknown4":FieldTypeInfo("uint8",None, False), "rootBoneIndex":FieldTypeInfo("uint16",None, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return REGNV3.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != REGNV3:
            raise Exception("%s is not of type %s but %s" % (id, "REGNV3", type(instance)))
        fieldId = id + ".unknown0"

        if (type(instance.unknown0) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".unknown1"

        if (type(instance.unknown1) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".firstVertexIndex"

        if (type(instance.firstVertexIndex) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".numberOfVertices"

        if (type(instance.numberOfVertices) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".firstFaceVertexIndexIndex"

        if (type(instance.firstFaceVertexIndexIndex) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".numberOfFaceVertexIndices"

        if (type(instance.numberOfFaceVertexIndices) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".numberOfBones"

        if (type(instance.numberOfBones) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".firstBoneLookupIndex"

        if (type(instance.firstBoneLookupIndex) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".numberOfBoneLookupIndices"

        if (type(instance.numberOfBoneLookupIndices) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".unknown2"

        if (type(instance.unknown2) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".unknown3"

        if (type(instance.unknown3) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".unknown4"

        if (type(instance.unknown4) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".rootBoneIndex"

        if (type(instance.rootBoneIndex) != int):
            raise Exception("%s is not an int" % (fieldId))


class BAT_V1:
    """"""
    fullName = "BAT_V1"
    tagName = "BAT_"
    tagVersion = 1
    size = 14
    structFormat = struct.Struct("<IHIHh")
    fields = ["unknown0", "regionIndex", "unknown1", "materialReferenceIndex", "unknown2"]

    def __setattr__(self, name, value):
        if name in ["unknown0", "regionIndex", "unknown1", "materialReferenceIndex", "unknown2"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["unknown0", "regionIndex", "unknown1", "materialReferenceIndex", "unknown2"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        pass #nothing to do
    
    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        pass #nothing to do

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert BAT_V1.size == BAT_V1.structFormat.size
            rawBytes = readable.read(BAT_V1.size)
        if rawBytes != None:
            l = BAT_V1.structFormat.unpack(rawBytes)
            self.unknown0 = l[0]
            if self.unknown0 != int(0):
             raise Exception("BAT_V1.unknown0 has value %s instead of the expected value int(0)" % self.unknown0)
            self.regionIndex = l[1]
            self.unknown1 = l[2]
            self.materialReferenceIndex = l[3]
            self.unknown2 = l[4]
        if (readable == None) and (rawBytes == None):
            self.unknown0 = int(0)
            self.unknown1 = 0
            self.unknown2 = -1
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + BAT_V1.size
        for i in range(count):
            list.append(BAT_V1(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += BAT_V1.size
        return list
    
    def toBytes(self):
        return BAT_V1.structFormat.pack(self.unknown0, self.regionIndex, self.unknown1, self.materialReferenceIndex, self.unknown2)
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(BAT_V1.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = BAT_V1.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += BAT_V1.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return BAT_V1.countOneOrMore(object) * BAT_V1.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"materialReferenceIndex": {}, "unknown1": {}, "unknown0": {}, "regionIndex": {}, "unknown2": {}}
    
    def getNamedBit(self, field, bitName):
        mask = BAT_V1.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = BAT_V1.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return BAT_V1.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"unknown0":FieldTypeInfo("uint32",None, False), "regionIndex":FieldTypeInfo("uint16",None, False), "unknown1":FieldTypeInfo("uint32",None, False), "materialReferenceIndex":FieldTypeInfo("uint16",None, False), "unknown2":FieldTypeInfo("int16",None, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return BAT_V1.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != BAT_V1:
            raise Exception("%s is not of type %s but %s" % (id, "BAT_V1", type(instance)))
        fieldId = id + ".unknown0"

        if (type(instance.unknown0) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".regionIndex"

        if (type(instance.regionIndex) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".unknown1"

        if (type(instance.unknown1) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".materialReferenceIndex"

        if (type(instance.materialReferenceIndex) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".unknown2"

        if (type(instance.unknown2) != int):
            raise Exception("%s is not an int" % (fieldId))


class MSECV1:
    """"""
    fullName = "MSECV1"
    tagName = "MSEC"
    tagVersion = 1
    size = 72
    structFormat = struct.Struct("<I68s")
    fields = ["unknown0", "boundingsAnimation"]

    def __setattr__(self, name, value):
        if name in ["unknown0", "boundingsAnimation"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["unknown0", "boundingsAnimation"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        pass #nothing to do
    
    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        pass #nothing to do

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert MSECV1.size == MSECV1.structFormat.size
            rawBytes = readable.read(MSECV1.size)
        if rawBytes != None:
            l = MSECV1.structFormat.unpack(rawBytes)
            self.unknown0 = l[0]
            self.boundingsAnimation = BNDSV0AnimationReference(rawBytes=l[1])
        if (readable == None) and (rawBytes == None):
            self.unknown0 = 0
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + MSECV1.size
        for i in range(count):
            list.append(MSECV1(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += MSECV1.size
        return list
    
    def toBytes(self):
        return MSECV1.structFormat.pack(self.unknown0, self.boundingsAnimation.toBytes())
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(MSECV1.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = MSECV1.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += MSECV1.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return MSECV1.countOneOrMore(object) * MSECV1.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"boundingsAnimation": {}, "unknown0": {}}
    
    def getNamedBit(self, field, bitName):
        mask = MSECV1.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = MSECV1.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return MSECV1.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"unknown0":FieldTypeInfo("uint32",None, False), "boundingsAnimation":FieldTypeInfo("BNDSV0AnimationReference",BNDSV0AnimationReference, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return MSECV1.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != MSECV1:
            raise Exception("%s is not of type %s but %s" % (id, "MSECV1", type(instance)))
        fieldId = id + ".unknown0"

        if (type(instance.unknown0) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".boundingsAnimation"

        BNDSV0AnimationReference.validateInstance(instance.boundingsAnimation, fieldId)


class DIV_V2:
    """Mesh Division"""
    fullName = "DIV_V2"
    tagName = "DIV_"
    tagVersion = 2
    size = 52
    structFormat = struct.Struct("<12s12s12s12sI")
    fields = ["faces", "regions", "objects", "msec", "unknown"]

    def __setattr__(self, name, value):
        if name in ["faces", "regions", "objects", "msec", "unknown"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["faces", "regions", "objects", "msec", "unknown"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    def resolveReferences(self, sections):
        self.faces = resolveRef(self.faces,sections,U16_V0,"DIV_V2.faces")
        self.regions = resolveRef(self.regions,sections,REGNV3,"DIV_V2.regions")
        self.objects = resolveRef(self.objects,sections,BAT_V1,"DIV_V2.objects")
        self.msec = resolveRef(self.msec,sections,MSECV1,"DIV_V2.msec")


    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        if oneOrMore.__class__ == [].__class__:
            for object in oneOrMore:
                object.resolveReferences(sections) 
        else:
            oneOrMore.resolveReferences(sections)

    def introduceIndexReferences(self, indexMaker):
        indexReference = indexMaker.getIndexReferenceTo(self.faces, Reference, U16_V0)
        U16_V0.introduceIndexReferencesForOneOrMore(self.faces,  indexMaker)
        self.faces = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.regions, Reference, REGNV3)
        REGNV3.introduceIndexReferencesForOneOrMore(self.regions,  indexMaker)
        self.regions = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.objects, Reference, BAT_V1)
        BAT_V1.introduceIndexReferencesForOneOrMore(self.objects,  indexMaker)
        self.objects = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.msec, Reference, MSECV1)
        MSECV1.introduceIndexReferencesForOneOrMore(self.msec,  indexMaker)
        self.msec = indexReference


    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        if object.__class__ == MD34IndexEntry:
            return # nothing to do (object was reachable trough 2 paths)
        if object.__class__ == [].__class__:
            for o in object:
                o.introduceIndexReferences(indexMaker) 
        else:
            object.introduceIndexReferences(indexMaker)

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert DIV_V2.size == DIV_V2.structFormat.size
            rawBytes = readable.read(DIV_V2.size)
        if rawBytes != None:
            l = DIV_V2.structFormat.unpack(rawBytes)
            self.faces = Reference(rawBytes=l[0])
            self.regions = Reference(rawBytes=l[1])
            self.objects = Reference(rawBytes=l[2])
            self.msec = Reference(rawBytes=l[3])
            self.unknown = l[4]
        if (readable == None) and (rawBytes == None):
            self.faces = U16_V0.createEmptyArray()
            self.regions = REGNV3.createEmptyArray()
            self.objects = BAT_V1.createEmptyArray()
            self.msec = MSECV1.createEmptyArray()
            self.unknown = 1
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + DIV_V2.size
        for i in range(count):
            list.append(DIV_V2(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += DIV_V2.size
        return list
    
    def toBytes(self):
        return DIV_V2.structFormat.pack(self.faces.toBytes(), self.regions.toBytes(), self.objects.toBytes(), self.msec.toBytes(), self.unknown)
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(DIV_V2.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = DIV_V2.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += DIV_V2.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return DIV_V2.countOneOrMore(object) * DIV_V2.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"regions": {}, "unknown": {}, "objects": {}, "msec": {}, "faces": {}}
    
    def getNamedBit(self, field, bitName):
        mask = DIV_V2.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = DIV_V2.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return DIV_V2.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"faces":FieldTypeInfo("U16_V0",U16_V0, True), "regions":FieldTypeInfo("REGNV3",REGNV3, True), "objects":FieldTypeInfo("BAT_V1",BAT_V1, True), "msec":FieldTypeInfo("MSECV1",MSECV1, True), "unknown":FieldTypeInfo("uint32",None, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return DIV_V2.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != DIV_V2:
            raise Exception("%s is not of type %s but %s" % (id, "DIV_V2", type(instance)))
        fieldId = id + ".faces"
        if (type(instance.faces) != list):
            raise Exception("%s is not a list of integers" % (fieldId))
        for itemIndex, item in enumerate(instance.faces):
            itemId = "%s[%d]" % (fieldId, itemIndex)
            if type(item) != int: 
                raise Exception("%s is not an integer" % (itemId))
            if (item < 0) or (item > 131071):
                raise Exception("%s has value %d which is not in range [0, 131071]"  % (itemId, item))
        fieldId = id + ".regions"

        if (type(instance.regions) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "REGNV3", type(instance.regions)))
        for itemIndex, item in enumerate(instance.regions):
            REGNV3.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".objects"

        if (type(instance.objects) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "BAT_V1", type(instance.objects)))
        for itemIndex, item in enumerate(instance.objects):
            BAT_V1.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".msec"

        if (type(instance.msec) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "MSECV1", type(instance.msec)))
        for itemIndex, item in enumerate(instance.msec):
            MSECV1.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".unknown"

        if (type(instance.unknown) != int):
            raise Exception("%s is not an int" % (fieldId))


class ATT_V1:
    """Attachment Point"""
    fullName = "ATT_V1"
    tagName = "ATT_"
    tagVersion = 1
    size = 20
    structFormat = struct.Struct("<i12sI")
    fields = ["unknown", "name", "bone"]

    def __setattr__(self, name, value):
        if name in ["unknown", "name", "bone"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["unknown", "name", "bone"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    def resolveReferences(self, sections):
        self.name = resolveRef(self.name,sections,CHARV0,"ATT_V1.name")


    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        if oneOrMore.__class__ == [].__class__:
            for object in oneOrMore:
                object.resolveReferences(sections) 
        else:
            oneOrMore.resolveReferences(sections)

    def introduceIndexReferences(self, indexMaker):
        indexReference = indexMaker.getIndexReferenceTo(self.name, Reference, CHARV0)
        CHARV0.introduceIndexReferencesForOneOrMore(self.name,  indexMaker)
        self.name = indexReference


    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        if object.__class__ == MD34IndexEntry:
            return # nothing to do (object was reachable trough 2 paths)
        if object.__class__ == [].__class__:
            for o in object:
                o.introduceIndexReferences(indexMaker) 
        else:
            object.introduceIndexReferences(indexMaker)

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert ATT_V1.size == ATT_V1.structFormat.size
            rawBytes = readable.read(ATT_V1.size)
        if rawBytes != None:
            l = ATT_V1.structFormat.unpack(rawBytes)
            self.unknown = l[0]
            if self.unknown != int(-1):
             raise Exception("ATT_V1.unknown has value %s instead of the expected value int(-1)" % self.unknown)
            self.name = Reference(rawBytes=l[1])
            self.bone = l[2]
        if (readable == None) and (rawBytes == None):
            self.unknown = int(-1)
            self.name = CHARV0.createEmptyArray()
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + ATT_V1.size
        for i in range(count):
            list.append(ATT_V1(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += ATT_V1.size
        return list
    
    def toBytes(self):
        return ATT_V1.structFormat.pack(self.unknown, self.name.toBytes(), self.bone)
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(ATT_V1.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = ATT_V1.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += ATT_V1.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return ATT_V1.countOneOrMore(object) * ATT_V1.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"unknown": {}, "name": {}, "bone": {}}
    
    def getNamedBit(self, field, bitName):
        mask = ATT_V1.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = ATT_V1.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return ATT_V1.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"unknown":FieldTypeInfo("int32",None, False), "name":FieldTypeInfo("CHARV0",CHARV0, True), "bone":FieldTypeInfo("uint32",None, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return ATT_V1.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != ATT_V1:
            raise Exception("%s is not of type %s but %s" % (id, "ATT_V1", type(instance)))
        fieldId = id + ".unknown"

        if (type(instance.unknown) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".name"

        if (instance.name != None) and (type(instance.name) != str):
            raise Exception("%s is not a string but a %s" % (fieldId, type(instance.name) ))
        fieldId = id + ".bone"

        if (type(instance.bone) != int):
            raise Exception("%s is not an int" % (fieldId))


class LITEV7:
    """Light types: 0=directional 1=point 2=spot, hotSpot expressed in radians"""
    fullName = "LITEV7"
    tagName = "LITE"
    tagVersion = 7
    size = 212
    structFormat = struct.Struct("<B1sB21s12s16s20s108sf8s20s")
    fields = ["lightType", "unknown1", "lightBone", "unknown2", "lightColor", "unknown3", "lightIntensity", "unknown4", "range", "unknown5", "hotSpot"]

    def __setattr__(self, name, value):
        if name in ["lightType", "unknown1", "lightBone", "unknown2", "lightColor", "unknown3", "lightIntensity", "unknown4", "range", "unknown5", "hotSpot"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["lightType", "unknown1", "lightBone", "unknown2", "lightColor", "unknown3", "lightIntensity", "unknown4", "range", "unknown5", "hotSpot"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        pass #nothing to do
    
    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        pass #nothing to do

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert LITEV7.size == LITEV7.structFormat.size
            rawBytes = readable.read(LITEV7.size)
        if rawBytes != None:
            l = LITEV7.structFormat.unpack(rawBytes)
            self.lightType = l[0]
            self.unknown1 = l[1]
            self.lightBone = l[2]
            self.unknown2 = l[3]
            self.lightColor = VEC3V0(rawBytes=l[4])
            self.unknown3 = l[5]
            self.lightIntensity = FloatAnimationReference(rawBytes=l[6])
            self.unknown4 = l[7]
            self.range = l[8]
            self.unknown5 = l[9]
            self.hotSpot = FloatAnimationReference(rawBytes=l[10])
        if (readable == None) and (rawBytes == None):
            self.unknown1 = bytes(1)
            self.unknown2 = bytes(21)
            self.unknown3 = bytes(16)
            self.unknown4 = bytes(108)
            self.unknown5 = bytes(8)
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + LITEV7.size
        for i in range(count):
            list.append(LITEV7(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += LITEV7.size
        return list
    
    def toBytes(self):
        return LITEV7.structFormat.pack(self.lightType, self.unknown1, self.lightBone, self.unknown2, self.lightColor.toBytes(), self.unknown3, self.lightIntensity.toBytes(), self.unknown4, self.range, self.unknown5, self.hotSpot.toBytes())
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(LITEV7.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = LITEV7.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += LITEV7.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return LITEV7.countOneOrMore(object) * LITEV7.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"lightColor": {}, "lightBone": {}, "lightType": {}, "hotSpot": {}, "unknown2": {}, "unknown3": {}, "range": {}, "unknown1": {}, "unknown4": {}, "unknown5": {}, "lightIntensity": {}}
    
    def getNamedBit(self, field, bitName):
        mask = LITEV7.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = LITEV7.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return LITEV7.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"lightType":FieldTypeInfo("uint8",None, False), "unknown1":FieldTypeInfo(None,None, False), "lightBone":FieldTypeInfo("uint8",None, False), "unknown2":FieldTypeInfo(None,None, False), "lightColor":FieldTypeInfo("VEC3V0",VEC3V0, False), "unknown3":FieldTypeInfo(None,None, False), "lightIntensity":FieldTypeInfo("FloatAnimationReference",FloatAnimationReference, False), "unknown4":FieldTypeInfo(None,None, False), "range":FieldTypeInfo("float",None, False), "unknown5":FieldTypeInfo(None,None, False), "hotSpot":FieldTypeInfo("FloatAnimationReference",FloatAnimationReference, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return LITEV7.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != LITEV7:
            raise Exception("%s is not of type %s but %s" % (id, "LITEV7", type(instance)))
        fieldId = id + ".lightType"

        if (type(instance.lightType) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".unknown1"

        if (type(instance.unknown1) != bytes) or (len(instance.unknown1) != 1):
            raise Exception("%s is not an bytes object of size %s" % (fieldId, "1"))
        fieldId = id + ".lightBone"

        if (type(instance.lightBone) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".unknown2"

        if (type(instance.unknown2) != bytes) or (len(instance.unknown2) != 21):
            raise Exception("%s is not an bytes object of size %s" % (fieldId, "21"))
        fieldId = id + ".lightColor"

        VEC3V0.validateInstance(instance.lightColor, fieldId)
        fieldId = id + ".unknown3"

        if (type(instance.unknown3) != bytes) or (len(instance.unknown3) != 16):
            raise Exception("%s is not an bytes object of size %s" % (fieldId, "16"))
        fieldId = id + ".lightIntensity"

        FloatAnimationReference.validateInstance(instance.lightIntensity, fieldId)
        fieldId = id + ".unknown4"

        if (type(instance.unknown4) != bytes) or (len(instance.unknown4) != 108):
            raise Exception("%s is not an bytes object of size %s" % (fieldId, "108"))
        fieldId = id + ".range"

        if (type(instance.range) != float):
            raise Exception("%s is not a float" % (fieldId))
        fieldId = id + ".unknown5"

        if (type(instance.unknown5) != bytes) or (len(instance.unknown5) != 8):
            raise Exception("%s is not an bytes object of size %s" % (fieldId, "8"))
        fieldId = id + ".hotSpot"

        FloatAnimationReference.validateInstance(instance.hotSpot, fieldId)


class MATMV0:
    """A reference to a material of a specified type"""
    fullName = "MATMV0"
    tagName = "MATM"
    tagVersion = 0
    size = 8
    structFormat = struct.Struct("<II")
    fields = ["materialType", "materialIndex"]

    def __setattr__(self, name, value):
        if name in ["materialType", "materialIndex"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["materialType", "materialIndex"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        pass #nothing to do
    
    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        pass #nothing to do

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert MATMV0.size == MATMV0.structFormat.size
            rawBytes = readable.read(MATMV0.size)
        if rawBytes != None:
            l = MATMV0.structFormat.unpack(rawBytes)
            self.materialType = l[0]
            self.materialIndex = l[1]
        if (readable == None) and (rawBytes == None):
            self.materialType = 1
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + MATMV0.size
        for i in range(count):
            list.append(MATMV0(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += MATMV0.size
        return list
    
    def toBytes(self):
        return MATMV0.structFormat.pack(self.materialType, self.materialIndex)
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(MATMV0.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = MATMV0.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += MATMV0.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return MATMV0.countOneOrMore(object) * MATMV0.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"materialIndex": {}, "materialType": {}}
    
    def getNamedBit(self, field, bitName):
        mask = MATMV0.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = MATMV0.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return MATMV0.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"materialType":FieldTypeInfo("uint32",None, False), "materialIndex":FieldTypeInfo("uint32",None, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return MATMV0.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != MATMV0:
            raise Exception("%s is not of type %s but %s" % (id, "MATMV0", type(instance)))
        fieldId = id + ".materialType"

        if (type(instance.materialType) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".materialIndex"

        if (type(instance.materialIndex) != int):
            raise Exception("%s is not an int" % (fieldId))


class PATUV4:
    """Unknown"""
    fullName = "PATUV4"
    tagName = "PATU"
    tagVersion = 4
    size = 152
    structFormat = struct.Struct("<152s")
    fields = ["unknown"]

    def __setattr__(self, name, value):
        if name in ["unknown"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["unknown"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        pass #nothing to do
    
    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        pass #nothing to do

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert PATUV4.size == PATUV4.structFormat.size
            rawBytes = readable.read(PATUV4.size)
        if rawBytes != None:
            l = PATUV4.structFormat.unpack(rawBytes)
            self.unknown = l[0]
        if (readable == None) and (rawBytes == None):
            self.unknown = bytes(152)
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + PATUV4.size
        for i in range(count):
            list.append(PATUV4(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += PATUV4.size
        return list
    
    def toBytes(self):
        return PATUV4.structFormat.pack(self.unknown)
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(PATUV4.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = PATUV4.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += PATUV4.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return PATUV4.countOneOrMore(object) * PATUV4.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"unknown": {}}
    
    def getNamedBit(self, field, bitName):
        mask = PATUV4.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = PATUV4.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return PATUV4.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"unknown":FieldTypeInfo(None,None, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return PATUV4.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != PATUV4:
            raise Exception("%s is not of type %s but %s" % (id, "PATUV4", type(instance)))
        fieldId = id + ".unknown"

        if (type(instance.unknown) != bytes) or (len(instance.unknown) != 152):
            raise Exception("%s is not an bytes object of size %s" % (fieldId, "152"))


class TRGDV0:
    """Unknown"""
    fullName = "TRGDV0"
    tagName = "TRGD"
    tagVersion = 0
    size = 24
    structFormat = struct.Struct("<12s12s")
    fields = ["unknown0", "name"]

    def __setattr__(self, name, value):
        if name in ["unknown0", "name"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["unknown0", "name"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    def resolveReferences(self, sections):
        self.unknown0 = resolveRef(self.unknown0,sections,U32_V0,"TRGDV0.unknown0")
        self.name = resolveRef(self.name,sections,CHARV0,"TRGDV0.name")


    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        if oneOrMore.__class__ == [].__class__:
            for object in oneOrMore:
                object.resolveReferences(sections) 
        else:
            oneOrMore.resolveReferences(sections)

    def introduceIndexReferences(self, indexMaker):
        indexReference = indexMaker.getIndexReferenceTo(self.unknown0, Reference, U32_V0)
        U32_V0.introduceIndexReferencesForOneOrMore(self.unknown0,  indexMaker)
        self.unknown0 = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.name, Reference, CHARV0)
        CHARV0.introduceIndexReferencesForOneOrMore(self.name,  indexMaker)
        self.name = indexReference


    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        if object.__class__ == MD34IndexEntry:
            return # nothing to do (object was reachable trough 2 paths)
        if object.__class__ == [].__class__:
            for o in object:
                o.introduceIndexReferences(indexMaker) 
        else:
            object.introduceIndexReferences(indexMaker)

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert TRGDV0.size == TRGDV0.structFormat.size
            rawBytes = readable.read(TRGDV0.size)
        if rawBytes != None:
            l = TRGDV0.structFormat.unpack(rawBytes)
            self.unknown0 = Reference(rawBytes=l[0])
            self.name = Reference(rawBytes=l[1])
        if (readable == None) and (rawBytes == None):
            self.unknown0 = U32_V0.createEmptyArray()
            self.name = CHARV0.createEmptyArray()
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + TRGDV0.size
        for i in range(count):
            list.append(TRGDV0(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += TRGDV0.size
        return list
    
    def toBytes(self):
        return TRGDV0.structFormat.pack(self.unknown0.toBytes(), self.name.toBytes())
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(TRGDV0.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = TRGDV0.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += TRGDV0.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return TRGDV0.countOneOrMore(object) * TRGDV0.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"unknown0": {}, "name": {}}
    
    def getNamedBit(self, field, bitName):
        mask = TRGDV0.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = TRGDV0.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return TRGDV0.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"unknown0":FieldTypeInfo("U32_V0",U32_V0, True), "name":FieldTypeInfo("CHARV0",CHARV0, True)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return TRGDV0.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != TRGDV0:
            raise Exception("%s is not of type %s but %s" % (id, "TRGDV0", type(instance)))
        fieldId = id + ".unknown0"
        if (type(instance.unknown0) != list):
            raise Exception("%s is not a list of integers" % (fieldId))
        for itemIndex, item in enumerate(instance.unknown0):
            itemId = "%s[%d]" % (fieldId, itemIndex)
            if type(item) != int: 
                raise Exception("%s is not an integer" % (itemId))
            if (item < 0) or (item > 8589934591):
                raise Exception("%s has value %d which is not in range [0, 8589934591]"  % (itemId, item))
        fieldId = id + ".name"

        if (instance.name != None) and (type(instance.name) != str):
            raise Exception("%s is not a string but a %s" % (fieldId, type(instance.name) ))


class LAYRV22:
    """Describes a layer of a material"""
    fullName = "LAYRV22"
    tagName = "LAYR"
    tagVersion = 22
    size = 356
    structFormat = struct.Struct("<I12s20sIII20s20sIi8si8s20s28s16s28s36s28s20s20s20siIffff")
    fields = ["unknown0", "imagePath", "color", "flags", "uvSource", "alphaFlags", "brightMult", "midtoneOffset", "unknown1", "unknown2", "unknown3", "unknown4", "unknown5", "unknown6", "unknown7", "unknown8", "uvOffset", "uvAngle", "uvTiling", "unknown9", "unknown10", "brightness", "unknown11", "tintFlags", "tintStrength", "tintStart", "tintCutout", "unknown15"]

    def __setattr__(self, name, value):
        if name in ["unknown0", "imagePath", "color", "flags", "uvSource", "alphaFlags", "brightMult", "midtoneOffset", "unknown1", "unknown2", "unknown3", "unknown4", "unknown5", "unknown6", "unknown7", "unknown8", "uvOffset", "uvAngle", "uvTiling", "unknown9", "unknown10", "brightness", "unknown11", "tintFlags", "tintStrength", "tintStart", "tintCutout", "unknown15"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["unknown0", "imagePath", "color", "flags", "uvSource", "alphaFlags", "brightMult", "midtoneOffset", "unknown1", "unknown2", "unknown3", "unknown4", "unknown5", "unknown6", "unknown7", "unknown8", "uvOffset", "uvAngle", "uvTiling", "unknown9", "unknown10", "brightness", "unknown11", "tintFlags", "tintStrength", "tintStart", "tintCutout", "unknown15"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    def resolveReferences(self, sections):
        self.imagePath = resolveRef(self.imagePath,sections,CHARV0,"LAYRV22.imagePath")


    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        if oneOrMore.__class__ == [].__class__:
            for object in oneOrMore:
                object.resolveReferences(sections) 
        else:
            oneOrMore.resolveReferences(sections)

    def introduceIndexReferences(self, indexMaker):
        indexReference = indexMaker.getIndexReferenceTo(self.imagePath, Reference, CHARV0)
        CHARV0.introduceIndexReferencesForOneOrMore(self.imagePath,  indexMaker)
        self.imagePath = indexReference


    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        if object.__class__ == MD34IndexEntry:
            return # nothing to do (object was reachable trough 2 paths)
        if object.__class__ == [].__class__:
            for o in object:
                o.introduceIndexReferences(indexMaker) 
        else:
            object.introduceIndexReferences(indexMaker)

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert LAYRV22.size == LAYRV22.structFormat.size
            rawBytes = readable.read(LAYRV22.size)
        if rawBytes != None:
            l = LAYRV22.structFormat.unpack(rawBytes)
            self.unknown0 = l[0]
            if self.unknown0 != int(0):
             raise Exception("LAYRV22.unknown0 has value %s instead of the expected value int(0)" % self.unknown0)
            self.imagePath = Reference(rawBytes=l[1])
            self.color = ColorAnimationReference(rawBytes=l[2])
            self.flags = l[3]
            self.uvSource = l[4]
            self.alphaFlags = l[5]
            self.brightMult = FloatAnimationReference(rawBytes=l[6])
            self.midtoneOffset = FloatAnimationReference(rawBytes=l[7])
            self.unknown1 = l[8]
            if self.unknown1 != int(0):
             raise Exception("LAYRV22.unknown1 has value %s instead of the expected value int(0)" % self.unknown1)
            self.unknown2 = l[9]
            if self.unknown2 != int(-1):
             raise Exception("LAYRV22.unknown2 has value %s instead of the expected value int(-1)" % self.unknown2)
            self.unknown3 = l[10]
            self.unknown4 = l[11]
            if self.unknown4 != int(0):
             raise Exception("LAYRV22.unknown4 has value %s instead of the expected value int(0)" % self.unknown4)
            self.unknown5 = l[12]
            self.unknown6 = UInt32AnimationReference(rawBytes=l[13])
            self.unknown7 = Vector2AnimationReference(rawBytes=l[14])
            self.unknown8 = UInt16AnimationReference(rawBytes=l[15])
            self.uvOffset = Vector2AnimationReference(rawBytes=l[16])
            self.uvAngle = Vector3AnimationReference(rawBytes=l[17])
            self.uvTiling = Vector2AnimationReference(rawBytes=l[18])
            self.unknown9 = UInt32AnimationReference(rawBytes=l[19])
            self.unknown10 = FloatAnimationReference(rawBytes=l[20])
            self.brightness = FloatAnimationReference(rawBytes=l[21])
            self.unknown11 = l[22]
            self.tintFlags = l[23]
            self.tintStrength = l[24]
            self.tintStart = l[25]
            self.tintCutout = l[26]
            self.unknown15 = l[27]
        if (readable == None) and (rawBytes == None):
            self.unknown0 = int(0)
            self.imagePath = CHARV0.createEmptyArray()
            self.flags = 0xec
            self.alphaFlags = 0
            self.unknown1 = int(0)
            self.unknown2 = int(-1)
            self.unknown3 = bytes(8)
            self.unknown4 = int(0)
            self.unknown5 = bytes(8)
            self.unknown11 = -1
            self.tintFlags = 0
            self.tintStrength = 4.0
            self.tintStart = 0.0
            self.tintCutout = 1.0
            self.unknown15 = 1.0
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + LAYRV22.size
        for i in range(count):
            list.append(LAYRV22(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += LAYRV22.size
        return list
    
    def toBytes(self):
        return LAYRV22.structFormat.pack(self.unknown0, self.imagePath.toBytes(), self.color.toBytes(), self.flags, self.uvSource, self.alphaFlags, self.brightMult.toBytes(), self.midtoneOffset.toBytes(), self.unknown1, self.unknown2, self.unknown3, self.unknown4, self.unknown5, self.unknown6.toBytes(), self.unknown7.toBytes(), self.unknown8.toBytes(), self.uvOffset.toBytes(), self.uvAngle.toBytes(), self.uvTiling.toBytes(), self.unknown9.toBytes(), self.unknown10.toBytes(), self.brightness.toBytes(), self.unknown11, self.tintFlags, self.tintStrength, self.tintStart, self.tintCutout, self.unknown15)
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(LAYRV22.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = LAYRV22.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += LAYRV22.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return LAYRV22.countOneOrMore(object) * LAYRV22.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"alphaFlags": {"alphaOnly":0x2, "alphaBasedShading":0x4, "colorEnabled":0x200, "useTint":0x1, "tintAlpha":0x2, "alphaAsTeamColor":0x1, "textureWrapY":0x8, "textureWrapX":0x4}, "color": {"alphaOnly":0x2, "alphaBasedShading":0x4, "colorEnabled":0x200, "useTint":0x1, "tintAlpha":0x2, "alphaAsTeamColor":0x1, "textureWrapY":0x8, "textureWrapX":0x4}, "uvTiling": {"alphaOnly":0x2, "alphaBasedShading":0x4, "colorEnabled":0x200, "useTint":0x1, "tintAlpha":0x2, "alphaAsTeamColor":0x1, "textureWrapY":0x8, "textureWrapX":0x4}, "uvSource": {"alphaOnly":0x2, "alphaBasedShading":0x4, "colorEnabled":0x200, "useTint":0x1, "tintAlpha":0x2, "alphaAsTeamColor":0x1, "textureWrapY":0x8, "textureWrapX":0x4}, "uvAngle": {"alphaOnly":0x2, "alphaBasedShading":0x4, "colorEnabled":0x200, "useTint":0x1, "tintAlpha":0x2, "alphaAsTeamColor":0x1, "textureWrapY":0x8, "textureWrapX":0x4}, "unknown2": {"alphaOnly":0x2, "alphaBasedShading":0x4, "colorEnabled":0x200, "useTint":0x1, "tintAlpha":0x2, "alphaAsTeamColor":0x1, "textureWrapY":0x8, "textureWrapX":0x4}, "unknown3": {"alphaOnly":0x2, "alphaBasedShading":0x4, "colorEnabled":0x200, "useTint":0x1, "tintAlpha":0x2, "alphaAsTeamColor":0x1, "textureWrapY":0x8, "textureWrapX":0x4}, "unknown0": {"alphaOnly":0x2, "alphaBasedShading":0x4, "colorEnabled":0x200, "useTint":0x1, "tintAlpha":0x2, "alphaAsTeamColor":0x1, "textureWrapY":0x8, "textureWrapX":0x4}, "unknown1": {"alphaOnly":0x2, "alphaBasedShading":0x4, "colorEnabled":0x200, "useTint":0x1, "tintAlpha":0x2, "alphaAsTeamColor":0x1, "textureWrapY":0x8, "textureWrapX":0x4}, "unknown6": {"alphaOnly":0x2, "alphaBasedShading":0x4, "colorEnabled":0x200, "useTint":0x1, "tintAlpha":0x2, "alphaAsTeamColor":0x1, "textureWrapY":0x8, "textureWrapX":0x4}, "unknown7": {"alphaOnly":0x2, "alphaBasedShading":0x4, "colorEnabled":0x200, "useTint":0x1, "tintAlpha":0x2, "alphaAsTeamColor":0x1, "textureWrapY":0x8, "textureWrapX":0x4}, "unknown4": {"alphaOnly":0x2, "alphaBasedShading":0x4, "colorEnabled":0x200, "useTint":0x1, "tintAlpha":0x2, "alphaAsTeamColor":0x1, "textureWrapY":0x8, "textureWrapX":0x4}, "unknown5": {"alphaOnly":0x2, "alphaBasedShading":0x4, "colorEnabled":0x200, "useTint":0x1, "tintAlpha":0x2, "alphaAsTeamColor":0x1, "textureWrapY":0x8, "textureWrapX":0x4}, "unknown8": {"alphaOnly":0x2, "alphaBasedShading":0x4, "colorEnabled":0x200, "useTint":0x1, "tintAlpha":0x2, "alphaAsTeamColor":0x1, "textureWrapY":0x8, "textureWrapX":0x4}, "unknown9": {"alphaOnly":0x2, "alphaBasedShading":0x4, "colorEnabled":0x200, "useTint":0x1, "tintAlpha":0x2, "alphaAsTeamColor":0x1, "textureWrapY":0x8, "textureWrapX":0x4}, "tintStart": {"alphaOnly":0x2, "alphaBasedShading":0x4, "colorEnabled":0x200, "useTint":0x1, "tintAlpha":0x2, "alphaAsTeamColor":0x1, "textureWrapY":0x8, "textureWrapX":0x4}, "tintCutout": {"alphaOnly":0x2, "alphaBasedShading":0x4, "colorEnabled":0x200, "useTint":0x1, "tintAlpha":0x2, "alphaAsTeamColor":0x1, "textureWrapY":0x8, "textureWrapX":0x4}, "imagePath": {"alphaOnly":0x2, "alphaBasedShading":0x4, "colorEnabled":0x200, "useTint":0x1, "tintAlpha":0x2, "alphaAsTeamColor":0x1, "textureWrapY":0x8, "textureWrapX":0x4}, "unknown10": {"alphaOnly":0x2, "alphaBasedShading":0x4, "colorEnabled":0x200, "useTint":0x1, "tintAlpha":0x2, "alphaAsTeamColor":0x1, "textureWrapY":0x8, "textureWrapX":0x4}, "unknown11": {"alphaOnly":0x2, "alphaBasedShading":0x4, "colorEnabled":0x200, "useTint":0x1, "tintAlpha":0x2, "alphaAsTeamColor":0x1, "textureWrapY":0x8, "textureWrapX":0x4}, "tintStrength": {"alphaOnly":0x2, "alphaBasedShading":0x4, "colorEnabled":0x200, "useTint":0x1, "tintAlpha":0x2, "alphaAsTeamColor":0x1, "textureWrapY":0x8, "textureWrapX":0x4}, "unknown15": {"alphaOnly":0x2, "alphaBasedShading":0x4, "colorEnabled":0x200, "useTint":0x1, "tintAlpha":0x2, "alphaAsTeamColor":0x1, "textureWrapY":0x8, "textureWrapX":0x4}, "uvOffset": {"alphaOnly":0x2, "alphaBasedShading":0x4, "colorEnabled":0x200, "useTint":0x1, "tintAlpha":0x2, "alphaAsTeamColor":0x1, "textureWrapY":0x8, "textureWrapX":0x4}, "brightMult": {"alphaOnly":0x2, "alphaBasedShading":0x4, "colorEnabled":0x200, "useTint":0x1, "tintAlpha":0x2, "alphaAsTeamColor":0x1, "textureWrapY":0x8, "textureWrapX":0x4}, "brightness": {"alphaOnly":0x2, "alphaBasedShading":0x4, "colorEnabled":0x200, "useTint":0x1, "tintAlpha":0x2, "alphaAsTeamColor":0x1, "textureWrapY":0x8, "textureWrapX":0x4}, "midtoneOffset": {"alphaOnly":0x2, "alphaBasedShading":0x4, "colorEnabled":0x200, "useTint":0x1, "tintAlpha":0x2, "alphaAsTeamColor":0x1, "textureWrapY":0x8, "textureWrapX":0x4}, "tintFlags": {"alphaOnly":0x2, "alphaBasedShading":0x4, "colorEnabled":0x200, "useTint":0x1, "tintAlpha":0x2, "alphaAsTeamColor":0x1, "textureWrapY":0x8, "textureWrapX":0x4}, "flags": {"alphaOnly":0x2, "alphaBasedShading":0x4, "colorEnabled":0x200, "useTint":0x1, "tintAlpha":0x2, "alphaAsTeamColor":0x1, "textureWrapY":0x8, "textureWrapX":0x4}}
    
    def getNamedBit(self, field, bitName):
        mask = LAYRV22.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = LAYRV22.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return LAYRV22.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"unknown0":FieldTypeInfo("uint32",None, False), "imagePath":FieldTypeInfo("CHARV0",CHARV0, True), "color":FieldTypeInfo("ColorAnimationReference",ColorAnimationReference, False), "flags":FieldTypeInfo("uint32",None, False), "uvSource":FieldTypeInfo("uint32",None, False), "alphaFlags":FieldTypeInfo("uint32",None, False), "brightMult":FieldTypeInfo("FloatAnimationReference",FloatAnimationReference, False), "midtoneOffset":FieldTypeInfo("FloatAnimationReference",FloatAnimationReference, False), "unknown1":FieldTypeInfo("uint32",None, False), "unknown2":FieldTypeInfo("int32",None, False), "unknown3":FieldTypeInfo(None,None, False), "unknown4":FieldTypeInfo("int32",None, False), "unknown5":FieldTypeInfo(None,None, False), "unknown6":FieldTypeInfo("UInt32AnimationReference",UInt32AnimationReference, False), "unknown7":FieldTypeInfo("Vector2AnimationReference",Vector2AnimationReference, False), "unknown8":FieldTypeInfo("UInt16AnimationReference",UInt16AnimationReference, False), "uvOffset":FieldTypeInfo("Vector2AnimationReference",Vector2AnimationReference, False), "uvAngle":FieldTypeInfo("Vector3AnimationReference",Vector3AnimationReference, False), "uvTiling":FieldTypeInfo("Vector2AnimationReference",Vector2AnimationReference, False), "unknown9":FieldTypeInfo("UInt32AnimationReference",UInt32AnimationReference, False), "unknown10":FieldTypeInfo("FloatAnimationReference",FloatAnimationReference, False), "brightness":FieldTypeInfo("FloatAnimationReference",FloatAnimationReference, False), "unknown11":FieldTypeInfo("int32",None, False), "tintFlags":FieldTypeInfo("uint32",None, False), "tintStrength":FieldTypeInfo("float",None, False), "tintStart":FieldTypeInfo("float",None, False), "tintCutout":FieldTypeInfo("float",None, False), "unknown15":FieldTypeInfo("float",None, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return LAYRV22.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != LAYRV22:
            raise Exception("%s is not of type %s but %s" % (id, "LAYRV22", type(instance)))
        fieldId = id + ".unknown0"

        if (type(instance.unknown0) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".imagePath"

        if (instance.imagePath != None) and (type(instance.imagePath) != str):
            raise Exception("%s is not a string but a %s" % (fieldId, type(instance.imagePath) ))
        fieldId = id + ".color"

        ColorAnimationReference.validateInstance(instance.color, fieldId)
        fieldId = id + ".flags"

        if (type(instance.flags) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".uvSource"

        if (type(instance.uvSource) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".alphaFlags"

        if (type(instance.alphaFlags) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".brightMult"

        FloatAnimationReference.validateInstance(instance.brightMult, fieldId)
        fieldId = id + ".midtoneOffset"

        FloatAnimationReference.validateInstance(instance.midtoneOffset, fieldId)
        fieldId = id + ".unknown1"

        if (type(instance.unknown1) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".unknown2"

        if (type(instance.unknown2) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".unknown3"

        if (type(instance.unknown3) != bytes) or (len(instance.unknown3) != 8):
            raise Exception("%s is not an bytes object of size %s" % (fieldId, "8"))
        fieldId = id + ".unknown4"

        if (type(instance.unknown4) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".unknown5"

        if (type(instance.unknown5) != bytes) or (len(instance.unknown5) != 8):
            raise Exception("%s is not an bytes object of size %s" % (fieldId, "8"))
        fieldId = id + ".unknown6"

        UInt32AnimationReference.validateInstance(instance.unknown6, fieldId)
        fieldId = id + ".unknown7"

        Vector2AnimationReference.validateInstance(instance.unknown7, fieldId)
        fieldId = id + ".unknown8"

        UInt16AnimationReference.validateInstance(instance.unknown8, fieldId)
        fieldId = id + ".uvOffset"

        Vector2AnimationReference.validateInstance(instance.uvOffset, fieldId)
        fieldId = id + ".uvAngle"

        Vector3AnimationReference.validateInstance(instance.uvAngle, fieldId)
        fieldId = id + ".uvTiling"

        Vector2AnimationReference.validateInstance(instance.uvTiling, fieldId)
        fieldId = id + ".unknown9"

        UInt32AnimationReference.validateInstance(instance.unknown9, fieldId)
        fieldId = id + ".unknown10"

        FloatAnimationReference.validateInstance(instance.unknown10, fieldId)
        fieldId = id + ".brightness"

        FloatAnimationReference.validateInstance(instance.brightness, fieldId)
        fieldId = id + ".unknown11"

        if (type(instance.unknown11) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".tintFlags"

        if (type(instance.tintFlags) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".tintStrength"

        if (type(instance.tintStrength) != float):
            raise Exception("%s is not a float" % (fieldId))
        fieldId = id + ".tintStart"

        if (type(instance.tintStart) != float):
            raise Exception("%s is not a float" % (fieldId))
        fieldId = id + ".tintCutout"

        if (type(instance.tintCutout) != float):
            raise Exception("%s is not a float" % (fieldId))
        fieldId = id + ".unknown15"

        if (type(instance.unknown15) != float):
            raise Exception("%s is not a float" % (fieldId))


class MAT_V15:
    """Standard Material"""
    fullName = "MAT_V15"
    tagName = "MAT_"
    tagVersion = 15
    size = 268
    structFormat = struct.Struct("<12sIIIiIfIIff12s12s12s12s12s12s12s12s12s12s12s12s12sIIIII20s20s")
    fields = ["name", "unknownFlags", "flags", "blendMode", "priority", "unknown1", "specularity", "unknown2", "cutoutThresh", "specMult", "emisMult", "diffuseLayer", "decalLayer", "specularLayer", "selfIllumLayer", "emissiveLayer", "reflectionLayer", "evioLayer", "evioMaskLayer", "alphaMaskLayer", "bumpLayer", "heightLayer", "layer12", "layer13", "unknown3", "layerBlendType", "emisBlendType", "emisMode", "specType", "unknownAnimationRef1", "unknownAnimationRef2"]

    def __setattr__(self, name, value):
        if name in ["name", "unknownFlags", "flags", "blendMode", "priority", "unknown1", "specularity", "unknown2", "cutoutThresh", "specMult", "emisMult", "diffuseLayer", "decalLayer", "specularLayer", "selfIllumLayer", "emissiveLayer", "reflectionLayer", "evioLayer", "evioMaskLayer", "alphaMaskLayer", "bumpLayer", "heightLayer", "layer12", "layer13", "unknown3", "layerBlendType", "emisBlendType", "emisMode", "specType", "unknownAnimationRef1", "unknownAnimationRef2"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["name", "unknownFlags", "flags", "blendMode", "priority", "unknown1", "specularity", "unknown2", "cutoutThresh", "specMult", "emisMult", "diffuseLayer", "decalLayer", "specularLayer", "selfIllumLayer", "emissiveLayer", "reflectionLayer", "evioLayer", "evioMaskLayer", "alphaMaskLayer", "bumpLayer", "heightLayer", "layer12", "layer13", "unknown3", "layerBlendType", "emisBlendType", "emisMode", "specType", "unknownAnimationRef1", "unknownAnimationRef2"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    def resolveReferences(self, sections):
        self.name = resolveRef(self.name,sections,CHARV0,"MAT_V15.name")
        self.diffuseLayer = resolveRef(self.diffuseLayer,sections,LAYRV22,"MAT_V15.diffuseLayer")
        self.decalLayer = resolveRef(self.decalLayer,sections,LAYRV22,"MAT_V15.decalLayer")
        self.specularLayer = resolveRef(self.specularLayer,sections,LAYRV22,"MAT_V15.specularLayer")
        self.selfIllumLayer = resolveRef(self.selfIllumLayer,sections,LAYRV22,"MAT_V15.selfIllumLayer")
        self.emissiveLayer = resolveRef(self.emissiveLayer,sections,LAYRV22,"MAT_V15.emissiveLayer")
        self.reflectionLayer = resolveRef(self.reflectionLayer,sections,LAYRV22,"MAT_V15.reflectionLayer")
        self.evioLayer = resolveRef(self.evioLayer,sections,LAYRV22,"MAT_V15.evioLayer")
        self.evioMaskLayer = resolveRef(self.evioMaskLayer,sections,LAYRV22,"MAT_V15.evioMaskLayer")
        self.alphaMaskLayer = resolveRef(self.alphaMaskLayer,sections,LAYRV22,"MAT_V15.alphaMaskLayer")
        self.bumpLayer = resolveRef(self.bumpLayer,sections,LAYRV22,"MAT_V15.bumpLayer")
        self.heightLayer = resolveRef(self.heightLayer,sections,LAYRV22,"MAT_V15.heightLayer")
        self.layer12 = resolveRef(self.layer12,sections,LAYRV22,"MAT_V15.layer12")
        self.layer13 = resolveRef(self.layer13,sections,LAYRV22,"MAT_V15.layer13")


    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        if oneOrMore.__class__ == [].__class__:
            for object in oneOrMore:
                object.resolveReferences(sections) 
        else:
            oneOrMore.resolveReferences(sections)

    def introduceIndexReferences(self, indexMaker):
        indexReference = indexMaker.getIndexReferenceTo(self.name, Reference, CHARV0)
        CHARV0.introduceIndexReferencesForOneOrMore(self.name,  indexMaker)
        self.name = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.diffuseLayer, Reference, LAYRV22)
        LAYRV22.introduceIndexReferencesForOneOrMore(self.diffuseLayer,  indexMaker)
        self.diffuseLayer = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.decalLayer, Reference, LAYRV22)
        LAYRV22.introduceIndexReferencesForOneOrMore(self.decalLayer,  indexMaker)
        self.decalLayer = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.specularLayer, Reference, LAYRV22)
        LAYRV22.introduceIndexReferencesForOneOrMore(self.specularLayer,  indexMaker)
        self.specularLayer = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.selfIllumLayer, Reference, LAYRV22)
        LAYRV22.introduceIndexReferencesForOneOrMore(self.selfIllumLayer,  indexMaker)
        self.selfIllumLayer = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.emissiveLayer, Reference, LAYRV22)
        LAYRV22.introduceIndexReferencesForOneOrMore(self.emissiveLayer,  indexMaker)
        self.emissiveLayer = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.reflectionLayer, Reference, LAYRV22)
        LAYRV22.introduceIndexReferencesForOneOrMore(self.reflectionLayer,  indexMaker)
        self.reflectionLayer = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.evioLayer, Reference, LAYRV22)
        LAYRV22.introduceIndexReferencesForOneOrMore(self.evioLayer,  indexMaker)
        self.evioLayer = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.evioMaskLayer, Reference, LAYRV22)
        LAYRV22.introduceIndexReferencesForOneOrMore(self.evioMaskLayer,  indexMaker)
        self.evioMaskLayer = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.alphaMaskLayer, Reference, LAYRV22)
        LAYRV22.introduceIndexReferencesForOneOrMore(self.alphaMaskLayer,  indexMaker)
        self.alphaMaskLayer = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.bumpLayer, Reference, LAYRV22)
        LAYRV22.introduceIndexReferencesForOneOrMore(self.bumpLayer,  indexMaker)
        self.bumpLayer = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.heightLayer, Reference, LAYRV22)
        LAYRV22.introduceIndexReferencesForOneOrMore(self.heightLayer,  indexMaker)
        self.heightLayer = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.layer12, Reference, LAYRV22)
        LAYRV22.introduceIndexReferencesForOneOrMore(self.layer12,  indexMaker)
        self.layer12 = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.layer13, Reference, LAYRV22)
        LAYRV22.introduceIndexReferencesForOneOrMore(self.layer13,  indexMaker)
        self.layer13 = indexReference


    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        if object.__class__ == MD34IndexEntry:
            return # nothing to do (object was reachable trough 2 paths)
        if object.__class__ == [].__class__:
            for o in object:
                o.introduceIndexReferences(indexMaker) 
        else:
            object.introduceIndexReferences(indexMaker)

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert MAT_V15.size == MAT_V15.structFormat.size
            rawBytes = readable.read(MAT_V15.size)
        if rawBytes != None:
            l = MAT_V15.structFormat.unpack(rawBytes)
            self.name = Reference(rawBytes=l[0])
            self.unknownFlags = l[1]
            self.flags = l[2]
            self.blendMode = l[3]
            self.priority = l[4]
            self.unknown1 = l[5]
            self.specularity = l[6]
            self.unknown2 = l[7]
            self.cutoutThresh = l[8]
            self.specMult = l[9]
            self.emisMult = l[10]
            self.diffuseLayer = Reference(rawBytes=l[11])
            self.decalLayer = Reference(rawBytes=l[12])
            self.specularLayer = Reference(rawBytes=l[13])
            self.selfIllumLayer = Reference(rawBytes=l[14])
            self.emissiveLayer = Reference(rawBytes=l[15])
            self.reflectionLayer = Reference(rawBytes=l[16])
            self.evioLayer = Reference(rawBytes=l[17])
            self.evioMaskLayer = Reference(rawBytes=l[18])
            self.alphaMaskLayer = Reference(rawBytes=l[19])
            self.bumpLayer = Reference(rawBytes=l[20])
            self.heightLayer = Reference(rawBytes=l[21])
            self.layer12 = Reference(rawBytes=l[22])
            self.layer13 = Reference(rawBytes=l[23])
            self.unknown3 = l[24]
            self.layerBlendType = l[25]
            self.emisBlendType = l[26]
            self.emisMode = l[27]
            self.specType = l[28]
            self.unknownAnimationRef1 = UInt32AnimationReference(rawBytes=l[29])
            self.unknownAnimationRef2 = UInt32AnimationReference(rawBytes=l[30])
        if (readable == None) and (rawBytes == None):
            self.name = CHARV0.createEmptyArray()
            self.unknownFlags = 0
            self.flags = 0
            self.unknown1 = 0
            self.unknown2 = 0
            self.cutoutThresh = 0
            self.specMult = 1.0
            self.emisMult = 1.0
            self.diffuseLayer = LAYRV22.createEmptyArray()
            self.decalLayer = LAYRV22.createEmptyArray()
            self.specularLayer = LAYRV22.createEmptyArray()
            self.selfIllumLayer = LAYRV22.createEmptyArray()
            self.emissiveLayer = LAYRV22.createEmptyArray()
            self.reflectionLayer = LAYRV22.createEmptyArray()
            self.evioLayer = LAYRV22.createEmptyArray()
            self.evioMaskLayer = LAYRV22.createEmptyArray()
            self.alphaMaskLayer = LAYRV22.createEmptyArray()
            self.bumpLayer = LAYRV22.createEmptyArray()
            self.heightLayer = LAYRV22.createEmptyArray()
            self.layer12 = LAYRV22.createEmptyArray()
            self.layer13 = LAYRV22.createEmptyArray()
            self.unknown3 = 0
            self.emisMode = 2
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + MAT_V15.size
        for i in range(count):
            list.append(MAT_V15(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += MAT_V15.size
        return list
    
    def toBytes(self):
        return MAT_V15.structFormat.pack(self.name.toBytes(), self.unknownFlags, self.flags, self.blendMode, self.priority, self.unknown1, self.specularity, self.unknown2, self.cutoutThresh, self.specMult, self.emisMult, self.diffuseLayer.toBytes(), self.decalLayer.toBytes(), self.specularLayer.toBytes(), self.selfIllumLayer.toBytes(), self.emissiveLayer.toBytes(), self.reflectionLayer.toBytes(), self.evioLayer.toBytes(), self.evioMaskLayer.toBytes(), self.alphaMaskLayer.toBytes(), self.bumpLayer.toBytes(), self.heightLayer.toBytes(), self.layer12.toBytes(), self.layer13.toBytes(), self.unknown3, self.layerBlendType, self.emisBlendType, self.emisMode, self.specType, self.unknownAnimationRef1.toBytes(), self.unknownAnimationRef2.toBytes())
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(MAT_V15.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = MAT_V15.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += MAT_V15.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return MAT_V15.countOneOrMore(object) * MAT_V15.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"specularLayer": {"splatUVfix":0x800, "twoSided":0x8, "useTerrainHDR":0x200, "noShadowsCast":0x20, "depthPrepass":0x100, "unknownFlag0x1":0x1, "unshaded":0x10, "noHitTest":0x40, "unknownFlag0x4":0x4, "noShadowsReceived":0x80, "unknownFlag0x8":0x8, "softBlending":0x1000, "forParticles":0x4000, "unknownFlag0x200":0x200, "unfogged":0x4}, "specularity": {"splatUVfix":0x800, "twoSided":0x8, "useTerrainHDR":0x200, "noShadowsCast":0x20, "depthPrepass":0x100, "unknownFlag0x1":0x1, "unshaded":0x10, "noHitTest":0x40, "unknownFlag0x4":0x4, "noShadowsReceived":0x80, "unknownFlag0x8":0x8, "softBlending":0x1000, "forParticles":0x4000, "unknownFlag0x200":0x200, "unfogged":0x4}, "unknownAnimationRef1": {"splatUVfix":0x800, "twoSided":0x8, "useTerrainHDR":0x200, "noShadowsCast":0x20, "depthPrepass":0x100, "unknownFlag0x1":0x1, "unshaded":0x10, "noHitTest":0x40, "unknownFlag0x4":0x4, "noShadowsReceived":0x80, "unknownFlag0x8":0x8, "softBlending":0x1000, "forParticles":0x4000, "unknownFlag0x200":0x200, "unfogged":0x4}, "emisMode": {"splatUVfix":0x800, "twoSided":0x8, "useTerrainHDR":0x200, "noShadowsCast":0x20, "depthPrepass":0x100, "unknownFlag0x1":0x1, "unshaded":0x10, "noHitTest":0x40, "unknownFlag0x4":0x4, "noShadowsReceived":0x80, "unknownFlag0x8":0x8, "softBlending":0x1000, "forParticles":0x4000, "unknownFlag0x200":0x200, "unfogged":0x4}, "specMult": {"splatUVfix":0x800, "twoSided":0x8, "useTerrainHDR":0x200, "noShadowsCast":0x20, "depthPrepass":0x100, "unknownFlag0x1":0x1, "unshaded":0x10, "noHitTest":0x40, "unknownFlag0x4":0x4, "noShadowsReceived":0x80, "unknownFlag0x8":0x8, "softBlending":0x1000, "forParticles":0x4000, "unknownFlag0x200":0x200, "unfogged":0x4}, "layer13": {"splatUVfix":0x800, "twoSided":0x8, "useTerrainHDR":0x200, "noShadowsCast":0x20, "depthPrepass":0x100, "unknownFlag0x1":0x1, "unshaded":0x10, "noHitTest":0x40, "unknownFlag0x4":0x4, "noShadowsReceived":0x80, "unknownFlag0x8":0x8, "softBlending":0x1000, "forParticles":0x4000, "unknownFlag0x200":0x200, "unfogged":0x4}, "layer12": {"splatUVfix":0x800, "twoSided":0x8, "useTerrainHDR":0x200, "noShadowsCast":0x20, "depthPrepass":0x100, "unknownFlag0x1":0x1, "unshaded":0x10, "noHitTest":0x40, "unknownFlag0x4":0x4, "noShadowsReceived":0x80, "unknownFlag0x8":0x8, "softBlending":0x1000, "forParticles":0x4000, "unknownFlag0x200":0x200, "unfogged":0x4}, "unknownFlags": {"splatUVfix":0x800, "twoSided":0x8, "useTerrainHDR":0x200, "noShadowsCast":0x20, "depthPrepass":0x100, "unknownFlag0x1":0x1, "unshaded":0x10, "noHitTest":0x40, "unknownFlag0x4":0x4, "noShadowsReceived":0x80, "unknownFlag0x8":0x8, "softBlending":0x1000, "forParticles":0x4000, "unknownFlag0x200":0x200, "unfogged":0x4}, "emisBlendType": {"splatUVfix":0x800, "twoSided":0x8, "useTerrainHDR":0x200, "noShadowsCast":0x20, "depthPrepass":0x100, "unknownFlag0x1":0x1, "unshaded":0x10, "noHitTest":0x40, "unknownFlag0x4":0x4, "noShadowsReceived":0x80, "unknownFlag0x8":0x8, "softBlending":0x1000, "forParticles":0x4000, "unknownFlag0x200":0x200, "unfogged":0x4}, "priority": {"splatUVfix":0x800, "twoSided":0x8, "useTerrainHDR":0x200, "noShadowsCast":0x20, "depthPrepass":0x100, "unknownFlag0x1":0x1, "unshaded":0x10, "noHitTest":0x40, "unknownFlag0x4":0x4, "noShadowsReceived":0x80, "unknownFlag0x8":0x8, "softBlending":0x1000, "forParticles":0x4000, "unknownFlag0x200":0x200, "unfogged":0x4}, "layerBlendType": {"splatUVfix":0x800, "twoSided":0x8, "useTerrainHDR":0x200, "noShadowsCast":0x20, "depthPrepass":0x100, "unknownFlag0x1":0x1, "unshaded":0x10, "noHitTest":0x40, "unknownFlag0x4":0x4, "noShadowsReceived":0x80, "unknownFlag0x8":0x8, "softBlending":0x1000, "forParticles":0x4000, "unknownFlag0x200":0x200, "unfogged":0x4}, "unknown2": {"splatUVfix":0x800, "twoSided":0x8, "useTerrainHDR":0x200, "noShadowsCast":0x20, "depthPrepass":0x100, "unknownFlag0x1":0x1, "unshaded":0x10, "noHitTest":0x40, "unknownFlag0x4":0x4, "noShadowsReceived":0x80, "unknownFlag0x8":0x8, "softBlending":0x1000, "forParticles":0x4000, "unknownFlag0x200":0x200, "unfogged":0x4}, "unknown3": {"splatUVfix":0x800, "twoSided":0x8, "useTerrainHDR":0x200, "noShadowsCast":0x20, "depthPrepass":0x100, "unknownFlag0x1":0x1, "unshaded":0x10, "noHitTest":0x40, "unknownFlag0x4":0x4, "noShadowsReceived":0x80, "unknownFlag0x8":0x8, "softBlending":0x1000, "forParticles":0x4000, "unknownFlag0x200":0x200, "unfogged":0x4}, "unknown1": {"splatUVfix":0x800, "twoSided":0x8, "useTerrainHDR":0x200, "noShadowsCast":0x20, "depthPrepass":0x100, "unknownFlag0x1":0x1, "unshaded":0x10, "noHitTest":0x40, "unknownFlag0x4":0x4, "noShadowsReceived":0x80, "unknownFlag0x8":0x8, "softBlending":0x1000, "forParticles":0x4000, "unknownFlag0x200":0x200, "unfogged":0x4}, "blendMode": {"splatUVfix":0x800, "twoSided":0x8, "useTerrainHDR":0x200, "noShadowsCast":0x20, "depthPrepass":0x100, "unknownFlag0x1":0x1, "unshaded":0x10, "noHitTest":0x40, "unknownFlag0x4":0x4, "noShadowsReceived":0x80, "unknownFlag0x8":0x8, "softBlending":0x1000, "forParticles":0x4000, "unknownFlag0x200":0x200, "unfogged":0x4}, "decalLayer": {"splatUVfix":0x800, "twoSided":0x8, "useTerrainHDR":0x200, "noShadowsCast":0x20, "depthPrepass":0x100, "unknownFlag0x1":0x1, "unshaded":0x10, "noHitTest":0x40, "unknownFlag0x4":0x4, "noShadowsReceived":0x80, "unknownFlag0x8":0x8, "softBlending":0x1000, "forParticles":0x4000, "unknownFlag0x200":0x200, "unfogged":0x4}, "diffuseLayer": {"splatUVfix":0x800, "twoSided":0x8, "useTerrainHDR":0x200, "noShadowsCast":0x20, "depthPrepass":0x100, "unknownFlag0x1":0x1, "unshaded":0x10, "noHitTest":0x40, "unknownFlag0x4":0x4, "noShadowsReceived":0x80, "unknownFlag0x8":0x8, "softBlending":0x1000, "forParticles":0x4000, "unknownFlag0x200":0x200, "unfogged":0x4}, "evioLayer": {"splatUVfix":0x800, "twoSided":0x8, "useTerrainHDR":0x200, "noShadowsCast":0x20, "depthPrepass":0x100, "unknownFlag0x1":0x1, "unshaded":0x10, "noHitTest":0x40, "unknownFlag0x4":0x4, "noShadowsReceived":0x80, "unknownFlag0x8":0x8, "softBlending":0x1000, "forParticles":0x4000, "unknownFlag0x200":0x200, "unfogged":0x4}, "cutoutThresh": {"splatUVfix":0x800, "twoSided":0x8, "useTerrainHDR":0x200, "noShadowsCast":0x20, "depthPrepass":0x100, "unknownFlag0x1":0x1, "unshaded":0x10, "noHitTest":0x40, "unknownFlag0x4":0x4, "noShadowsReceived":0x80, "unknownFlag0x8":0x8, "softBlending":0x1000, "forParticles":0x4000, "unknownFlag0x200":0x200, "unfogged":0x4}, "specType": {"splatUVfix":0x800, "twoSided":0x8, "useTerrainHDR":0x200, "noShadowsCast":0x20, "depthPrepass":0x100, "unknownFlag0x1":0x1, "unshaded":0x10, "noHitTest":0x40, "unknownFlag0x4":0x4, "noShadowsReceived":0x80, "unknownFlag0x8":0x8, "softBlending":0x1000, "forParticles":0x4000, "unknownFlag0x200":0x200, "unfogged":0x4}, "selfIllumLayer": {"splatUVfix":0x800, "twoSided":0x8, "useTerrainHDR":0x200, "noShadowsCast":0x20, "depthPrepass":0x100, "unknownFlag0x1":0x1, "unshaded":0x10, "noHitTest":0x40, "unknownFlag0x4":0x4, "noShadowsReceived":0x80, "unknownFlag0x8":0x8, "softBlending":0x1000, "forParticles":0x4000, "unknownFlag0x200":0x200, "unfogged":0x4}, "emissiveLayer": {"splatUVfix":0x800, "twoSided":0x8, "useTerrainHDR":0x200, "noShadowsCast":0x20, "depthPrepass":0x100, "unknownFlag0x1":0x1, "unshaded":0x10, "noHitTest":0x40, "unknownFlag0x4":0x4, "noShadowsReceived":0x80, "unknownFlag0x8":0x8, "softBlending":0x1000, "forParticles":0x4000, "unknownFlag0x200":0x200, "unfogged":0x4}, "reflectionLayer": {"splatUVfix":0x800, "twoSided":0x8, "useTerrainHDR":0x200, "noShadowsCast":0x20, "depthPrepass":0x100, "unknownFlag0x1":0x1, "unshaded":0x10, "noHitTest":0x40, "unknownFlag0x4":0x4, "noShadowsReceived":0x80, "unknownFlag0x8":0x8, "softBlending":0x1000, "forParticles":0x4000, "unknownFlag0x200":0x200, "unfogged":0x4}, "alphaMaskLayer": {"splatUVfix":0x800, "twoSided":0x8, "useTerrainHDR":0x200, "noShadowsCast":0x20, "depthPrepass":0x100, "unknownFlag0x1":0x1, "unshaded":0x10, "noHitTest":0x40, "unknownFlag0x4":0x4, "noShadowsReceived":0x80, "unknownFlag0x8":0x8, "softBlending":0x1000, "forParticles":0x4000, "unknownFlag0x200":0x200, "unfogged":0x4}, "bumpLayer": {"splatUVfix":0x800, "twoSided":0x8, "useTerrainHDR":0x200, "noShadowsCast":0x20, "depthPrepass":0x100, "unknownFlag0x1":0x1, "unshaded":0x10, "noHitTest":0x40, "unknownFlag0x4":0x4, "noShadowsReceived":0x80, "unknownFlag0x8":0x8, "softBlending":0x1000, "forParticles":0x4000, "unknownFlag0x200":0x200, "unfogged":0x4}, "name": {"splatUVfix":0x800, "twoSided":0x8, "useTerrainHDR":0x200, "noShadowsCast":0x20, "depthPrepass":0x100, "unknownFlag0x1":0x1, "unshaded":0x10, "noHitTest":0x40, "unknownFlag0x4":0x4, "noShadowsReceived":0x80, "unknownFlag0x8":0x8, "softBlending":0x1000, "forParticles":0x4000, "unknownFlag0x200":0x200, "unfogged":0x4}, "emisMult": {"splatUVfix":0x800, "twoSided":0x8, "useTerrainHDR":0x200, "noShadowsCast":0x20, "depthPrepass":0x100, "unknownFlag0x1":0x1, "unshaded":0x10, "noHitTest":0x40, "unknownFlag0x4":0x4, "noShadowsReceived":0x80, "unknownFlag0x8":0x8, "softBlending":0x1000, "forParticles":0x4000, "unknownFlag0x200":0x200, "unfogged":0x4}, "evioMaskLayer": {"splatUVfix":0x800, "twoSided":0x8, "useTerrainHDR":0x200, "noShadowsCast":0x20, "depthPrepass":0x100, "unknownFlag0x1":0x1, "unshaded":0x10, "noHitTest":0x40, "unknownFlag0x4":0x4, "noShadowsReceived":0x80, "unknownFlag0x8":0x8, "softBlending":0x1000, "forParticles":0x4000, "unknownFlag0x200":0x200, "unfogged":0x4}, "unknownAnimationRef2": {"splatUVfix":0x800, "twoSided":0x8, "useTerrainHDR":0x200, "noShadowsCast":0x20, "depthPrepass":0x100, "unknownFlag0x1":0x1, "unshaded":0x10, "noHitTest":0x40, "unknownFlag0x4":0x4, "noShadowsReceived":0x80, "unknownFlag0x8":0x8, "softBlending":0x1000, "forParticles":0x4000, "unknownFlag0x200":0x200, "unfogged":0x4}, "flags": {"splatUVfix":0x800, "twoSided":0x8, "useTerrainHDR":0x200, "noShadowsCast":0x20, "depthPrepass":0x100, "unknownFlag0x1":0x1, "unshaded":0x10, "noHitTest":0x40, "unknownFlag0x4":0x4, "noShadowsReceived":0x80, "unknownFlag0x8":0x8, "softBlending":0x1000, "forParticles":0x4000, "unknownFlag0x200":0x200, "unfogged":0x4}, "heightLayer": {"splatUVfix":0x800, "twoSided":0x8, "useTerrainHDR":0x200, "noShadowsCast":0x20, "depthPrepass":0x100, "unknownFlag0x1":0x1, "unshaded":0x10, "noHitTest":0x40, "unknownFlag0x4":0x4, "noShadowsReceived":0x80, "unknownFlag0x8":0x8, "softBlending":0x1000, "forParticles":0x4000, "unknownFlag0x200":0x200, "unfogged":0x4}}
    
    def getNamedBit(self, field, bitName):
        mask = MAT_V15.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = MAT_V15.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return MAT_V15.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"name":FieldTypeInfo("CHARV0",CHARV0, True), "unknownFlags":FieldTypeInfo("uint32",None, False), "flags":FieldTypeInfo("uint32",None, False), "blendMode":FieldTypeInfo("uint32",None, False), "priority":FieldTypeInfo("int32",None, False), "unknown1":FieldTypeInfo("uint32",None, False), "specularity":FieldTypeInfo("float",None, False), "unknown2":FieldTypeInfo("uint32",None, False), "cutoutThresh":FieldTypeInfo("uint32",None, False), "specMult":FieldTypeInfo("float",None, False), "emisMult":FieldTypeInfo("float",None, False), "diffuseLayer":FieldTypeInfo("LAYRV22",LAYRV22, True), "decalLayer":FieldTypeInfo("LAYRV22",LAYRV22, True), "specularLayer":FieldTypeInfo("LAYRV22",LAYRV22, True), "selfIllumLayer":FieldTypeInfo("LAYRV22",LAYRV22, True), "emissiveLayer":FieldTypeInfo("LAYRV22",LAYRV22, True), "reflectionLayer":FieldTypeInfo("LAYRV22",LAYRV22, True), "evioLayer":FieldTypeInfo("LAYRV22",LAYRV22, True), "evioMaskLayer":FieldTypeInfo("LAYRV22",LAYRV22, True), "alphaMaskLayer":FieldTypeInfo("LAYRV22",LAYRV22, True), "bumpLayer":FieldTypeInfo("LAYRV22",LAYRV22, True), "heightLayer":FieldTypeInfo("LAYRV22",LAYRV22, True), "layer12":FieldTypeInfo("LAYRV22",LAYRV22, True), "layer13":FieldTypeInfo("LAYRV22",LAYRV22, True), "unknown3":FieldTypeInfo("uint32",None, False), "layerBlendType":FieldTypeInfo("uint32",None, False), "emisBlendType":FieldTypeInfo("uint32",None, False), "emisMode":FieldTypeInfo("uint32",None, False), "specType":FieldTypeInfo("uint32",None, False), "unknownAnimationRef1":FieldTypeInfo("UInt32AnimationReference",UInt32AnimationReference, False), "unknownAnimationRef2":FieldTypeInfo("UInt32AnimationReference",UInt32AnimationReference, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return MAT_V15.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != MAT_V15:
            raise Exception("%s is not of type %s but %s" % (id, "MAT_V15", type(instance)))
        fieldId = id + ".name"

        if (instance.name != None) and (type(instance.name) != str):
            raise Exception("%s is not a string but a %s" % (fieldId, type(instance.name) ))
        fieldId = id + ".unknownFlags"

        if (type(instance.unknownFlags) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".flags"

        if (type(instance.flags) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".blendMode"

        if (type(instance.blendMode) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".priority"

        if (type(instance.priority) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".unknown1"

        if (type(instance.unknown1) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".specularity"

        if (type(instance.specularity) != float):
            raise Exception("%s is not a float" % (fieldId))
        fieldId = id + ".unknown2"

        if (type(instance.unknown2) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".cutoutThresh"

        if (type(instance.cutoutThresh) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".specMult"

        if (type(instance.specMult) != float):
            raise Exception("%s is not a float" % (fieldId))
        fieldId = id + ".emisMult"

        if (type(instance.emisMult) != float):
            raise Exception("%s is not a float" % (fieldId))
        fieldId = id + ".diffuseLayer"

        if (type(instance.diffuseLayer) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "LAYRV22", type(instance.diffuseLayer)))
        for itemIndex, item in enumerate(instance.diffuseLayer):
            LAYRV22.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".decalLayer"

        if (type(instance.decalLayer) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "LAYRV22", type(instance.decalLayer)))
        for itemIndex, item in enumerate(instance.decalLayer):
            LAYRV22.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".specularLayer"

        if (type(instance.specularLayer) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "LAYRV22", type(instance.specularLayer)))
        for itemIndex, item in enumerate(instance.specularLayer):
            LAYRV22.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".selfIllumLayer"

        if (type(instance.selfIllumLayer) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "LAYRV22", type(instance.selfIllumLayer)))
        for itemIndex, item in enumerate(instance.selfIllumLayer):
            LAYRV22.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".emissiveLayer"

        if (type(instance.emissiveLayer) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "LAYRV22", type(instance.emissiveLayer)))
        for itemIndex, item in enumerate(instance.emissiveLayer):
            LAYRV22.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".reflectionLayer"

        if (type(instance.reflectionLayer) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "LAYRV22", type(instance.reflectionLayer)))
        for itemIndex, item in enumerate(instance.reflectionLayer):
            LAYRV22.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".evioLayer"

        if (type(instance.evioLayer) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "LAYRV22", type(instance.evioLayer)))
        for itemIndex, item in enumerate(instance.evioLayer):
            LAYRV22.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".evioMaskLayer"

        if (type(instance.evioMaskLayer) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "LAYRV22", type(instance.evioMaskLayer)))
        for itemIndex, item in enumerate(instance.evioMaskLayer):
            LAYRV22.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".alphaMaskLayer"

        if (type(instance.alphaMaskLayer) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "LAYRV22", type(instance.alphaMaskLayer)))
        for itemIndex, item in enumerate(instance.alphaMaskLayer):
            LAYRV22.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".bumpLayer"

        if (type(instance.bumpLayer) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "LAYRV22", type(instance.bumpLayer)))
        for itemIndex, item in enumerate(instance.bumpLayer):
            LAYRV22.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".heightLayer"

        if (type(instance.heightLayer) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "LAYRV22", type(instance.heightLayer)))
        for itemIndex, item in enumerate(instance.heightLayer):
            LAYRV22.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".layer12"

        if (type(instance.layer12) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "LAYRV22", type(instance.layer12)))
        for itemIndex, item in enumerate(instance.layer12):
            LAYRV22.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".layer13"

        if (type(instance.layer13) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "LAYRV22", type(instance.layer13)))
        for itemIndex, item in enumerate(instance.layer13):
            LAYRV22.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".unknown3"

        if (type(instance.unknown3) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".layerBlendType"

        if (type(instance.layerBlendType) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".emisBlendType"

        if (type(instance.emisBlendType) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".emisMode"

        if (type(instance.emisMode) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".specType"

        if (type(instance.specType) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".unknownAnimationRef1"

        UInt32AnimationReference.validateInstance(instance.unknownAnimationRef1, fieldId)
        fieldId = id + ".unknownAnimationRef2"

        UInt32AnimationReference.validateInstance(instance.unknownAnimationRef2, fieldId)


class DIS_V4:
    """
                Displacement Material
            """
    fullName = "DIS_V4"
    tagName = "DIS_"
    tagVersion = 4
    size = 68
    structFormat = struct.Struct("<12sI20s12s12sII")
    fields = ["name", "unknown0", "strengthFactor", "normalLayer", "strengthLayer", "flags", "priority"]

    def __setattr__(self, name, value):
        if name in ["name", "unknown0", "strengthFactor", "normalLayer", "strengthLayer", "flags", "priority"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["name", "unknown0", "strengthFactor", "normalLayer", "strengthLayer", "flags", "priority"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    def resolveReferences(self, sections):
        self.name = resolveRef(self.name,sections,CHARV0,"DIS_V4.name")
        self.normalLayer = resolveRef(self.normalLayer,sections,LAYRV22,"DIS_V4.normalLayer")
        self.strengthLayer = resolveRef(self.strengthLayer,sections,LAYRV22,"DIS_V4.strengthLayer")


    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        if oneOrMore.__class__ == [].__class__:
            for object in oneOrMore:
                object.resolveReferences(sections) 
        else:
            oneOrMore.resolveReferences(sections)

    def introduceIndexReferences(self, indexMaker):
        indexReference = indexMaker.getIndexReferenceTo(self.name, Reference, CHARV0)
        CHARV0.introduceIndexReferencesForOneOrMore(self.name,  indexMaker)
        self.name = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.normalLayer, Reference, LAYRV22)
        LAYRV22.introduceIndexReferencesForOneOrMore(self.normalLayer,  indexMaker)
        self.normalLayer = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.strengthLayer, Reference, LAYRV22)
        LAYRV22.introduceIndexReferencesForOneOrMore(self.strengthLayer,  indexMaker)
        self.strengthLayer = indexReference


    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        if object.__class__ == MD34IndexEntry:
            return # nothing to do (object was reachable trough 2 paths)
        if object.__class__ == [].__class__:
            for o in object:
                o.introduceIndexReferences(indexMaker) 
        else:
            object.introduceIndexReferences(indexMaker)

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert DIS_V4.size == DIS_V4.structFormat.size
            rawBytes = readable.read(DIS_V4.size)
        if rawBytes != None:
            l = DIS_V4.structFormat.unpack(rawBytes)
            self.name = Reference(rawBytes=l[0])
            self.unknown0 = l[1]
            if self.unknown0 != int(0):
             raise Exception("DIS_V4.unknown0 has value %s instead of the expected value int(0)" % self.unknown0)
            self.strengthFactor = FloatAnimationReference(rawBytes=l[2])
            self.normalLayer = Reference(rawBytes=l[3])
            self.strengthLayer = Reference(rawBytes=l[4])
            self.flags = l[5]
            self.priority = l[6]
        if (readable == None) and (rawBytes == None):
            self.name = CHARV0.createEmptyArray()
            self.unknown0 = int(0)
            self.normalLayer = LAYRV22.createEmptyArray()
            self.strengthLayer = LAYRV22.createEmptyArray()
            self.flags = 0
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + DIS_V4.size
        for i in range(count):
            list.append(DIS_V4(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += DIS_V4.size
        return list
    
    def toBytes(self):
        return DIS_V4.structFormat.pack(self.name.toBytes(), self.unknown0, self.strengthFactor.toBytes(), self.normalLayer.toBytes(), self.strengthLayer.toBytes(), self.flags, self.priority)
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(DIS_V4.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = DIS_V4.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += DIS_V4.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return DIS_V4.countOneOrMore(object) * DIS_V4.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"strengthFactor": {}, "name": {}, "normalLayer": {}, "priority": {}, "unknown0": {}, "strengthLayer": {}, "flags": {}}
    
    def getNamedBit(self, field, bitName):
        mask = DIS_V4.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = DIS_V4.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return DIS_V4.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"name":FieldTypeInfo("CHARV0",CHARV0, True), "unknown0":FieldTypeInfo("uint32",None, False), "strengthFactor":FieldTypeInfo("FloatAnimationReference",FloatAnimationReference, False), "normalLayer":FieldTypeInfo("LAYRV22",LAYRV22, True), "strengthLayer":FieldTypeInfo("LAYRV22",LAYRV22, True), "flags":FieldTypeInfo("uint32",None, False), "priority":FieldTypeInfo("uint32",None, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return DIS_V4.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != DIS_V4:
            raise Exception("%s is not of type %s but %s" % (id, "DIS_V4", type(instance)))
        fieldId = id + ".name"

        if (instance.name != None) and (type(instance.name) != str):
            raise Exception("%s is not a string but a %s" % (fieldId, type(instance.name) ))
        fieldId = id + ".unknown0"

        if (type(instance.unknown0) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".strengthFactor"

        FloatAnimationReference.validateInstance(instance.strengthFactor, fieldId)
        fieldId = id + ".normalLayer"

        if (type(instance.normalLayer) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "LAYRV22", type(instance.normalLayer)))
        for itemIndex, item in enumerate(instance.normalLayer):
            LAYRV22.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".strengthLayer"

        if (type(instance.strengthLayer) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "LAYRV22", type(instance.strengthLayer)))
        for itemIndex, item in enumerate(instance.strengthLayer):
            LAYRV22.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".flags"

        if (type(instance.flags) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".priority"

        if (type(instance.priority) != int):
            raise Exception("%s is not an int" % (fieldId))


class CMS_V0:
    """Composite Material Section"""
    fullName = "CMS_V0"
    tagName = "CMS_"
    tagVersion = 0
    size = 24
    structFormat = struct.Struct("<I20s")
    fields = ["materialReferenceIndex", "alphaFactor"]

    def __setattr__(self, name, value):
        if name in ["materialReferenceIndex", "alphaFactor"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["materialReferenceIndex", "alphaFactor"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        pass #nothing to do
    
    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        pass #nothing to do

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert CMS_V0.size == CMS_V0.structFormat.size
            rawBytes = readable.read(CMS_V0.size)
        if rawBytes != None:
            l = CMS_V0.structFormat.unpack(rawBytes)
            self.materialReferenceIndex = l[0]
            self.alphaFactor = FloatAnimationReference(rawBytes=l[1])
        if (readable == None) and (rawBytes == None):
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + CMS_V0.size
        for i in range(count):
            list.append(CMS_V0(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += CMS_V0.size
        return list
    
    def toBytes(self):
        return CMS_V0.structFormat.pack(self.materialReferenceIndex, self.alphaFactor.toBytes())
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(CMS_V0.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = CMS_V0.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += CMS_V0.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return CMS_V0.countOneOrMore(object) * CMS_V0.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"materialReferenceIndex": {}, "alphaFactor": {}}
    
    def getNamedBit(self, field, bitName):
        mask = CMS_V0.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = CMS_V0.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return CMS_V0.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"materialReferenceIndex":FieldTypeInfo("uint32",None, False), "alphaFactor":FieldTypeInfo("FloatAnimationReference",FloatAnimationReference, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return CMS_V0.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != CMS_V0:
            raise Exception("%s is not of type %s but %s" % (id, "CMS_V0", type(instance)))
        fieldId = id + ".materialReferenceIndex"

        if (type(instance.materialReferenceIndex) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".alphaFactor"

        FloatAnimationReference.validateInstance(instance.alphaFactor, fieldId)


class CMP_V2:
    """Composite Material"""
    fullName = "CMP_V2"
    tagName = "CMP_"
    tagVersion = 2
    size = 28
    structFormat = struct.Struct("<12sI12s")
    fields = ["name", "unknown", "sections"]

    def __setattr__(self, name, value):
        if name in ["name", "unknown", "sections"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["name", "unknown", "sections"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    def resolveReferences(self, sections):
        self.name = resolveRef(self.name,sections,CHARV0,"CMP_V2.name")
        self.sections = resolveRef(self.sections,sections,CMS_V0,"CMP_V2.sections")


    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        if oneOrMore.__class__ == [].__class__:
            for object in oneOrMore:
                object.resolveReferences(sections) 
        else:
            oneOrMore.resolveReferences(sections)

    def introduceIndexReferences(self, indexMaker):
        indexReference = indexMaker.getIndexReferenceTo(self.name, Reference, CHARV0)
        CHARV0.introduceIndexReferencesForOneOrMore(self.name,  indexMaker)
        self.name = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.sections, Reference, CMS_V0)
        CMS_V0.introduceIndexReferencesForOneOrMore(self.sections,  indexMaker)
        self.sections = indexReference


    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        if object.__class__ == MD34IndexEntry:
            return # nothing to do (object was reachable trough 2 paths)
        if object.__class__ == [].__class__:
            for o in object:
                o.introduceIndexReferences(indexMaker) 
        else:
            object.introduceIndexReferences(indexMaker)

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert CMP_V2.size == CMP_V2.structFormat.size
            rawBytes = readable.read(CMP_V2.size)
        if rawBytes != None:
            l = CMP_V2.structFormat.unpack(rawBytes)
            self.name = Reference(rawBytes=l[0])
            self.unknown = l[1]
            if self.unknown != int(0):
             raise Exception("CMP_V2.unknown has value %s instead of the expected value int(0)" % self.unknown)
            self.sections = Reference(rawBytes=l[2])
        if (readable == None) and (rawBytes == None):
            self.name = CHARV0.createEmptyArray()
            self.unknown = int(0)
            self.sections = CMS_V0.createEmptyArray()
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + CMP_V2.size
        for i in range(count):
            list.append(CMP_V2(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += CMP_V2.size
        return list
    
    def toBytes(self):
        return CMP_V2.structFormat.pack(self.name.toBytes(), self.unknown, self.sections.toBytes())
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(CMP_V2.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = CMP_V2.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += CMP_V2.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return CMP_V2.countOneOrMore(object) * CMP_V2.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"unknown": {}, "sections": {}, "name": {}}
    
    def getNamedBit(self, field, bitName):
        mask = CMP_V2.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = CMP_V2.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return CMP_V2.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"name":FieldTypeInfo("CHARV0",CHARV0, True), "unknown":FieldTypeInfo("uint32",None, False), "sections":FieldTypeInfo("CMS_V0",CMS_V0, True)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return CMP_V2.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != CMP_V2:
            raise Exception("%s is not of type %s but %s" % (id, "CMP_V2", type(instance)))
        fieldId = id + ".name"

        if (instance.name != None) and (type(instance.name) != str):
            raise Exception("%s is not a string but a %s" % (fieldId, type(instance.name) ))
        fieldId = id + ".unknown"

        if (type(instance.unknown) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".sections"

        if (type(instance.sections) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "CMS_V0", type(instance.sections)))
        for itemIndex, item in enumerate(instance.sections):
            CMS_V0.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))


class TER_V0:
    """Terrain Material"""
    fullName = "TER_V0"
    tagName = "TER_"
    tagVersion = 0
    size = 24
    structFormat = struct.Struct("<12s12s")
    fields = ["name", "layer"]

    def __setattr__(self, name, value):
        if name in ["name", "layer"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["name", "layer"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    def resolveReferences(self, sections):
        self.name = resolveRef(self.name,sections,CHARV0,"TER_V0.name")
        self.layer = resolveRef(self.layer,sections,LAYRV22,"TER_V0.layer")


    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        if oneOrMore.__class__ == [].__class__:
            for object in oneOrMore:
                object.resolveReferences(sections) 
        else:
            oneOrMore.resolveReferences(sections)

    def introduceIndexReferences(self, indexMaker):
        indexReference = indexMaker.getIndexReferenceTo(self.name, Reference, CHARV0)
        CHARV0.introduceIndexReferencesForOneOrMore(self.name,  indexMaker)
        self.name = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.layer, Reference, LAYRV22)
        LAYRV22.introduceIndexReferencesForOneOrMore(self.layer,  indexMaker)
        self.layer = indexReference


    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        if object.__class__ == MD34IndexEntry:
            return # nothing to do (object was reachable trough 2 paths)
        if object.__class__ == [].__class__:
            for o in object:
                o.introduceIndexReferences(indexMaker) 
        else:
            object.introduceIndexReferences(indexMaker)

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert TER_V0.size == TER_V0.structFormat.size
            rawBytes = readable.read(TER_V0.size)
        if rawBytes != None:
            l = TER_V0.structFormat.unpack(rawBytes)
            self.name = Reference(rawBytes=l[0])
            self.layer = Reference(rawBytes=l[1])
        if (readable == None) and (rawBytes == None):
            self.name = CHARV0.createEmptyArray()
            self.layer = LAYRV22.createEmptyArray()
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + TER_V0.size
        for i in range(count):
            list.append(TER_V0(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += TER_V0.size
        return list
    
    def toBytes(self):
        return TER_V0.structFormat.pack(self.name.toBytes(), self.layer.toBytes())
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(TER_V0.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = TER_V0.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += TER_V0.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return TER_V0.countOneOrMore(object) * TER_V0.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"layer": {}, "name": {}}
    
    def getNamedBit(self, field, bitName):
        mask = TER_V0.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = TER_V0.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return TER_V0.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"name":FieldTypeInfo("CHARV0",CHARV0, True), "layer":FieldTypeInfo("LAYRV22",LAYRV22, True)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return TER_V0.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != TER_V0:
            raise Exception("%s is not of type %s but %s" % (id, "TER_V0", type(instance)))
        fieldId = id + ".name"

        if (instance.name != None) and (type(instance.name) != str):
            raise Exception("%s is not a string but a %s" % (fieldId, type(instance.name) ))
        fieldId = id + ".layer"

        if (type(instance.layer) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "LAYRV22", type(instance.layer)))
        for itemIndex, item in enumerate(instance.layer):
            LAYRV22.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))


class VOL_V0:
    """Volume Material"""
    fullName = "VOL_V0"
    tagName = "VOL_"
    tagVersion = 0
    size = 84
    structFormat = struct.Struct("<12sI4sIIfff12s12s12s4s4s")
    fields = ["name", "unknown", "unknownSection1", "unknownSection4", "unknownSection9", "volumeDensity", "unknownSection7", "unknownSection8", "colorDefiningLayer", "unknownLayer2", "unknownLayer3", "unknownSection2", "unknownSection3"]

    def __setattr__(self, name, value):
        if name in ["name", "unknown", "unknownSection1", "unknownSection4", "unknownSection9", "volumeDensity", "unknownSection7", "unknownSection8", "colorDefiningLayer", "unknownLayer2", "unknownLayer3", "unknownSection2", "unknownSection3"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["name", "unknown", "unknownSection1", "unknownSection4", "unknownSection9", "volumeDensity", "unknownSection7", "unknownSection8", "colorDefiningLayer", "unknownLayer2", "unknownLayer3", "unknownSection2", "unknownSection3"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    def resolveReferences(self, sections):
        self.name = resolveRef(self.name,sections,CHARV0,"VOL_V0.name")
        self.colorDefiningLayer = resolveRef(self.colorDefiningLayer,sections,LAYRV22,"VOL_V0.colorDefiningLayer")
        self.unknownLayer2 = resolveRef(self.unknownLayer2,sections,LAYRV22,"VOL_V0.unknownLayer2")
        self.unknownLayer3 = resolveRef(self.unknownLayer3,sections,LAYRV22,"VOL_V0.unknownLayer3")


    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        if oneOrMore.__class__ == [].__class__:
            for object in oneOrMore:
                object.resolveReferences(sections) 
        else:
            oneOrMore.resolveReferences(sections)

    def introduceIndexReferences(self, indexMaker):
        indexReference = indexMaker.getIndexReferenceTo(self.name, Reference, CHARV0)
        CHARV0.introduceIndexReferencesForOneOrMore(self.name,  indexMaker)
        self.name = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.colorDefiningLayer, Reference, LAYRV22)
        LAYRV22.introduceIndexReferencesForOneOrMore(self.colorDefiningLayer,  indexMaker)
        self.colorDefiningLayer = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.unknownLayer2, Reference, LAYRV22)
        LAYRV22.introduceIndexReferencesForOneOrMore(self.unknownLayer2,  indexMaker)
        self.unknownLayer2 = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.unknownLayer3, Reference, LAYRV22)
        LAYRV22.introduceIndexReferencesForOneOrMore(self.unknownLayer3,  indexMaker)
        self.unknownLayer3 = indexReference


    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        if object.__class__ == MD34IndexEntry:
            return # nothing to do (object was reachable trough 2 paths)
        if object.__class__ == [].__class__:
            for o in object:
                o.introduceIndexReferences(indexMaker) 
        else:
            object.introduceIndexReferences(indexMaker)

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert VOL_V0.size == VOL_V0.structFormat.size
            rawBytes = readable.read(VOL_V0.size)
        if rawBytes != None:
            l = VOL_V0.structFormat.unpack(rawBytes)
            self.name = Reference(rawBytes=l[0])
            self.unknown = l[1]
            self.unknownSection1 = l[2]
            self.unknownSection4 = l[3]
            self.unknownSection9 = l[4]
            self.volumeDensity = l[5]
            self.unknownSection7 = l[6]
            self.unknownSection8 = l[7]
            self.colorDefiningLayer = Reference(rawBytes=l[8])
            self.unknownLayer2 = Reference(rawBytes=l[9])
            self.unknownLayer3 = Reference(rawBytes=l[10])
            self.unknownSection2 = l[11]
            self.unknownSection3 = l[12]
        if (readable == None) and (rawBytes == None):
            self.name = CHARV0.createEmptyArray()
            self.unknown = 0
            self.unknownSection1 = bytes(4)
            self.colorDefiningLayer = LAYRV22.createEmptyArray()
            self.unknownLayer2 = LAYRV22.createEmptyArray()
            self.unknownLayer3 = LAYRV22.createEmptyArray()
            self.unknownSection2 = bytes(4)
            self.unknownSection3 = bytes(4)
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + VOL_V0.size
        for i in range(count):
            list.append(VOL_V0(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += VOL_V0.size
        return list
    
    def toBytes(self):
        return VOL_V0.structFormat.pack(self.name.toBytes(), self.unknown, self.unknownSection1, self.unknownSection4, self.unknownSection9, self.volumeDensity, self.unknownSection7, self.unknownSection8, self.colorDefiningLayer.toBytes(), self.unknownLayer2.toBytes(), self.unknownLayer3.toBytes(), self.unknownSection2, self.unknownSection3)
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(VOL_V0.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = VOL_V0.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += VOL_V0.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return VOL_V0.countOneOrMore(object) * VOL_V0.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"unknownSection8": {}, "unknownSection9": {}, "name": {}, "unknownLayer2": {}, "unknown": {}, "colorDefiningLayer": {}, "unknownSection1": {}, "unknownSection7": {}, "unknownSection4": {}, "volumeDensity": {}, "unknownSection2": {}, "unknownLayer3": {}, "unknownSection3": {}}
    
    def getNamedBit(self, field, bitName):
        mask = VOL_V0.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = VOL_V0.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return VOL_V0.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"name":FieldTypeInfo("CHARV0",CHARV0, True), "unknown":FieldTypeInfo("uint32",None, False), "unknownSection1":FieldTypeInfo(None,None, False), "unknownSection4":FieldTypeInfo("uint32",None, False), "unknownSection9":FieldTypeInfo("uint32",None, False), "volumeDensity":FieldTypeInfo("float",None, False), "unknownSection7":FieldTypeInfo("float",None, False), "unknownSection8":FieldTypeInfo("float",None, False), "colorDefiningLayer":FieldTypeInfo("LAYRV22",LAYRV22, True), "unknownLayer2":FieldTypeInfo("LAYRV22",LAYRV22, True), "unknownLayer3":FieldTypeInfo("LAYRV22",LAYRV22, True), "unknownSection2":FieldTypeInfo(None,None, False), "unknownSection3":FieldTypeInfo(None,None, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return VOL_V0.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != VOL_V0:
            raise Exception("%s is not of type %s but %s" % (id, "VOL_V0", type(instance)))
        fieldId = id + ".name"

        if (instance.name != None) and (type(instance.name) != str):
            raise Exception("%s is not a string but a %s" % (fieldId, type(instance.name) ))
        fieldId = id + ".unknown"

        if (type(instance.unknown) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".unknownSection1"

        if (type(instance.unknownSection1) != bytes) or (len(instance.unknownSection1) != 4):
            raise Exception("%s is not an bytes object of size %s" % (fieldId, "4"))
        fieldId = id + ".unknownSection4"

        if (type(instance.unknownSection4) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".unknownSection9"

        if (type(instance.unknownSection9) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".volumeDensity"

        if (type(instance.volumeDensity) != float):
            raise Exception("%s is not a float" % (fieldId))
        fieldId = id + ".unknownSection7"

        if (type(instance.unknownSection7) != float):
            raise Exception("%s is not a float" % (fieldId))
        fieldId = id + ".unknownSection8"

        if (type(instance.unknownSection8) != float):
            raise Exception("%s is not a float" % (fieldId))
        fieldId = id + ".colorDefiningLayer"

        if (type(instance.colorDefiningLayer) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "LAYRV22", type(instance.colorDefiningLayer)))
        for itemIndex, item in enumerate(instance.colorDefiningLayer):
            LAYRV22.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".unknownLayer2"

        if (type(instance.unknownLayer2) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "LAYRV22", type(instance.unknownLayer2)))
        for itemIndex, item in enumerate(instance.unknownLayer2):
            LAYRV22.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".unknownLayer3"

        if (type(instance.unknownLayer3) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "LAYRV22", type(instance.unknownLayer3)))
        for itemIndex, item in enumerate(instance.unknownLayer3):
            LAYRV22.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".unknownSection2"

        if (type(instance.unknownSection2) != bytes) or (len(instance.unknownSection2) != 4):
            raise Exception("%s is not an bytes object of size %s" % (fieldId, "4"))
        fieldId = id + ".unknownSection3"

        if (type(instance.unknownSection3) != bytes) or (len(instance.unknownSection3) != 4):
            raise Exception("%s is not an bytes object of size %s" % (fieldId, "4"))


class PAR_V12:
    """Particle System"""
    fullName = "PAR_V12"
    tagName = "PAR_"
    tagVersion = 12
    size = 1316
    structFormat = struct.Struct("<II20s20sI20s20s20s20s20s20sIIIIfffff36s36s20s20s20sfffffIIIffffII20sI36s36s20s20sII36sI36sI20s20s20sI16sBBBBfHHffffi24sf8sf416sI44s20s48s12s")
    fields = ["bone", "materialReferenceIndex", "emissionSpeed1", "emissionSpeed2", "randomizeWithEmissionSpeed2", "emissionAngleX", "emissionAngleY", "emissionSpreadX", "emissionSpreadY", "lifespan1", "lifespan2", "randomizeWithLifespan2", "unknown0", "unknown1", "unknown2", "zAcceleration", "unknownFloat1a", "unknownFloat1b", "unknownFloat1c", "unknownFloat1d", "particleSizes1", "rotationValues1", "initialColor1", "finalColor1", "unknownColor1", "slowdown", "unknownFloat2a", "unknownFloat2b", "unknownFloat2c", "unknown4", "trailingEnabled", "unknown5", "unknown6", "unknownFloat3a", "unknownFloat3b", "unknownFloat3c", "unknownFloat3d", "indexPlusHighestIndex", "maxParticles", "emissionRate", "emissionAreaType", "emissionAreaSize", "tailUnk1", "emissionAreaRadius", "spreadUnk", "emissionType", "randomizeWithParticleSizes2", "particleSizes2", "randomizeWithRotationValues2", "rotationValues2", "randomizeWithColor2", "initialColor2", "finalColor2", "unknownColor2", "unknown7", "partEmit", "phase1StartImageIndex", "phase1EndImageIndex", "phase2EndImageIndex", "phase2StartImageIndex", "relativePhase1Length", "numberOfColumns", "numberOfRows", "columnWidth", "rowHeight", "unknownFloat4", "unknownFloat5", "unknown9", "unknown10", "unknownFloat6", "unknown11", "unknownFloat7", "unknown12", "flags", "unknown13", "ar1", "unknown14", "copyIndices"]

    def __setattr__(self, name, value):
        if name in ["bone", "materialReferenceIndex", "emissionSpeed1", "emissionSpeed2", "randomizeWithEmissionSpeed2", "emissionAngleX", "emissionAngleY", "emissionSpreadX", "emissionSpreadY", "lifespan1", "lifespan2", "randomizeWithLifespan2", "unknown0", "unknown1", "unknown2", "zAcceleration", "unknownFloat1a", "unknownFloat1b", "unknownFloat1c", "unknownFloat1d", "particleSizes1", "rotationValues1", "initialColor1", "finalColor1", "unknownColor1", "slowdown", "unknownFloat2a", "unknownFloat2b", "unknownFloat2c", "unknown4", "trailingEnabled", "unknown5", "unknown6", "unknownFloat3a", "unknownFloat3b", "unknownFloat3c", "unknownFloat3d", "indexPlusHighestIndex", "maxParticles", "emissionRate", "emissionAreaType", "emissionAreaSize", "tailUnk1", "emissionAreaRadius", "spreadUnk", "emissionType", "randomizeWithParticleSizes2", "particleSizes2", "randomizeWithRotationValues2", "rotationValues2", "randomizeWithColor2", "initialColor2", "finalColor2", "unknownColor2", "unknown7", "partEmit", "phase1StartImageIndex", "phase1EndImageIndex", "phase2EndImageIndex", "phase2StartImageIndex", "relativePhase1Length", "numberOfColumns", "numberOfRows", "columnWidth", "rowHeight", "unknownFloat4", "unknownFloat5", "unknown9", "unknown10", "unknownFloat6", "unknown11", "unknownFloat7", "unknown12", "flags", "unknown13", "ar1", "unknown14", "copyIndices"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["bone", "materialReferenceIndex", "emissionSpeed1", "emissionSpeed2", "randomizeWithEmissionSpeed2", "emissionAngleX", "emissionAngleY", "emissionSpreadX", "emissionSpreadY", "lifespan1", "lifespan2", "randomizeWithLifespan2", "unknown0", "unknown1", "unknown2", "zAcceleration", "unknownFloat1a", "unknownFloat1b", "unknownFloat1c", "unknownFloat1d", "particleSizes1", "rotationValues1", "initialColor1", "finalColor1", "unknownColor1", "slowdown", "unknownFloat2a", "unknownFloat2b", "unknownFloat2c", "unknown4", "trailingEnabled", "unknown5", "unknown6", "unknownFloat3a", "unknownFloat3b", "unknownFloat3c", "unknownFloat3d", "indexPlusHighestIndex", "maxParticles", "emissionRate", "emissionAreaType", "emissionAreaSize", "tailUnk1", "emissionAreaRadius", "spreadUnk", "emissionType", "randomizeWithParticleSizes2", "particleSizes2", "randomizeWithRotationValues2", "rotationValues2", "randomizeWithColor2", "initialColor2", "finalColor2", "unknownColor2", "unknown7", "partEmit", "phase1StartImageIndex", "phase1EndImageIndex", "phase2EndImageIndex", "phase2StartImageIndex", "relativePhase1Length", "numberOfColumns", "numberOfRows", "columnWidth", "rowHeight", "unknownFloat4", "unknownFloat5", "unknown9", "unknown10", "unknownFloat6", "unknown11", "unknownFloat7", "unknown12", "flags", "unknown13", "ar1", "unknown14", "copyIndices"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    def resolveReferences(self, sections):
        self.copyIndices = resolveRef(self.copyIndices,sections,U32_V0,"PAR_V12.copyIndices")


    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        if oneOrMore.__class__ == [].__class__:
            for object in oneOrMore:
                object.resolveReferences(sections) 
        else:
            oneOrMore.resolveReferences(sections)

    def introduceIndexReferences(self, indexMaker):
        indexReference = indexMaker.getIndexReferenceTo(self.copyIndices, Reference, U32_V0)
        U32_V0.introduceIndexReferencesForOneOrMore(self.copyIndices,  indexMaker)
        self.copyIndices = indexReference


    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        if object.__class__ == MD34IndexEntry:
            return # nothing to do (object was reachable trough 2 paths)
        if object.__class__ == [].__class__:
            for o in object:
                o.introduceIndexReferences(indexMaker) 
        else:
            object.introduceIndexReferences(indexMaker)

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert PAR_V12.size == PAR_V12.structFormat.size
            rawBytes = readable.read(PAR_V12.size)
        if rawBytes != None:
            l = PAR_V12.structFormat.unpack(rawBytes)
            self.bone = l[0]
            self.materialReferenceIndex = l[1]
            self.emissionSpeed1 = FloatAnimationReference(rawBytes=l[2])
            self.emissionSpeed2 = FloatAnimationReference(rawBytes=l[3])
            self.randomizeWithEmissionSpeed2 = l[4]
            self.emissionAngleX = FloatAnimationReference(rawBytes=l[5])
            self.emissionAngleY = FloatAnimationReference(rawBytes=l[6])
            self.emissionSpreadX = FloatAnimationReference(rawBytes=l[7])
            self.emissionSpreadY = FloatAnimationReference(rawBytes=l[8])
            self.lifespan1 = FloatAnimationReference(rawBytes=l[9])
            self.lifespan2 = FloatAnimationReference(rawBytes=l[10])
            self.randomizeWithLifespan2 = l[11]
            self.unknown0 = l[12]
            if self.unknown0 != int(0):
             raise Exception("PAR_V12.unknown0 has value %s instead of the expected value int(0)" % self.unknown0)
            self.unknown1 = l[13]
            if self.unknown1 != int(0):
             raise Exception("PAR_V12.unknown1 has value %s instead of the expected value int(0)" % self.unknown1)
            self.unknown2 = l[14]
            if self.unknown2 != int(0):
             raise Exception("PAR_V12.unknown2 has value %s instead of the expected value int(0)" % self.unknown2)
            self.zAcceleration = l[15]
            self.unknownFloat1a = l[16]
            self.unknownFloat1b = l[17]
            self.unknownFloat1c = l[18]
            self.unknownFloat1d = l[19]
            self.particleSizes1 = Vector3AnimationReference(rawBytes=l[20])
            self.rotationValues1 = Vector3AnimationReference(rawBytes=l[21])
            self.initialColor1 = ColorAnimationReference(rawBytes=l[22])
            self.finalColor1 = ColorAnimationReference(rawBytes=l[23])
            self.unknownColor1 = ColorAnimationReference(rawBytes=l[24])
            self.slowdown = l[25]
            self.unknownFloat2a = l[26]
            self.unknownFloat2b = l[27]
            self.unknownFloat2c = l[28]
            self.unknown4 = l[29]
            self.trailingEnabled = l[30]
            self.unknown5 = l[31]
            self.unknown6 = l[32]
            self.unknownFloat3a = l[33]
            self.unknownFloat3b = l[34]
            self.unknownFloat3c = l[35]
            self.unknownFloat3d = l[36]
            self.indexPlusHighestIndex = l[37]
            self.maxParticles = l[38]
            self.emissionRate = FloatAnimationReference(rawBytes=l[39])
            self.emissionAreaType = l[40]
            self.emissionAreaSize = Vector3AnimationReference(rawBytes=l[41])
            self.tailUnk1 = Vector3AnimationReference(rawBytes=l[42])
            self.emissionAreaRadius = FloatAnimationReference(rawBytes=l[43])
            self.spreadUnk = FloatAnimationReference(rawBytes=l[44])
            self.emissionType = l[45]
            self.randomizeWithParticleSizes2 = l[46]
            self.particleSizes2 = Vector3AnimationReference(rawBytes=l[47])
            self.randomizeWithRotationValues2 = l[48]
            self.rotationValues2 = Vector3AnimationReference(rawBytes=l[49])
            self.randomizeWithColor2 = l[50]
            self.initialColor2 = ColorAnimationReference(rawBytes=l[51])
            self.finalColor2 = ColorAnimationReference(rawBytes=l[52])
            self.unknownColor2 = ColorAnimationReference(rawBytes=l[53])
            self.unknown7 = l[54]
            self.partEmit = Int16AnimationReference(rawBytes=l[55])
            self.phase1StartImageIndex = l[56]
            self.phase1EndImageIndex = l[57]
            self.phase2EndImageIndex = l[58]
            self.phase2StartImageIndex = l[59]
            if self.phase2StartImageIndex != int(0):
             raise Exception("PAR_V12.phase2StartImageIndex has value %s instead of the expected value int(0)" % self.phase2StartImageIndex)
            self.relativePhase1Length = l[60]
            self.numberOfColumns = l[61]
            self.numberOfRows = l[62]
            self.columnWidth = l[63]
            self.rowHeight = l[64]
            self.unknownFloat4 = l[65]
            self.unknownFloat5 = l[66]
            self.unknown9 = l[67]
            self.unknown10 = l[68]
            self.unknownFloat6 = l[69]
            self.unknown11 = l[70]
            self.unknownFloat7 = l[71]
            if self.unknownFloat7 != 1.0:
             raise Exception("PAR_V12.unknownFloat7 has value %s instead of the expected value 1.0" % self.unknownFloat7)
            self.unknown12 = l[72]
            self.flags = l[73]
            self.unknown13 = l[74]
            self.ar1 = FloatAnimationReference(rawBytes=l[75])
            self.unknown14 = l[76]
            self.copyIndices = Reference(rawBytes=l[77])
        if (readable == None) and (rawBytes == None):
            self.unknown0 = int(0)
            self.unknown1 = int(0)
            self.unknown2 = int(0)
            self.unknownFloat1b = 1.0
            self.unknownFloat1c = 1.0
            self.unknownFloat1d = 1.0
            self.unknownFloat2a = 0.0
            self.unknownFloat2b = 1.0
            self.unknownFloat2c = 1.0
            self.unknown4 = 0.0
            self.unknown5 = 0
            self.unknown6 = 0
            self.unknownFloat3a = 0.0
            self.unknownFloat3b = 0.0
            self.unknownFloat3c = 0.0
            self.unknownFloat3d = 0.1
            self.unknown7 = 0
            self.phase1StartImageIndex = 0
            self.phase1EndImageIndex = 0
            self.phase2EndImageIndex = 0
            self.phase2StartImageIndex = int(0)
            self.columnWidth = float("inf")
            self.rowHeight = float("inf")
            self.unknownFloat4 = 0.0
            self.unknownFloat5 = 1.0
            self.unknown9 = -1
            self.unknown10 = bytes(24)
            self.unknownFloat6 = 1.0
            self.unknown11 = bytes(8)
            self.unknownFloat7 = 1.0
            self.unknown12 = bytes(416)
            self.flags = 0
            self.unknown13 = bytes(44)
            self.unknown14 = bytes(48)
            self.copyIndices = U32_V0.createEmptyArray()
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + PAR_V12.size
        for i in range(count):
            list.append(PAR_V12(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += PAR_V12.size
        return list
    
    def toBytes(self):
        return PAR_V12.structFormat.pack(self.bone, self.materialReferenceIndex, self.emissionSpeed1.toBytes(), self.emissionSpeed2.toBytes(), self.randomizeWithEmissionSpeed2, self.emissionAngleX.toBytes(), self.emissionAngleY.toBytes(), self.emissionSpreadX.toBytes(), self.emissionSpreadY.toBytes(), self.lifespan1.toBytes(), self.lifespan2.toBytes(), self.randomizeWithLifespan2, self.unknown0, self.unknown1, self.unknown2, self.zAcceleration, self.unknownFloat1a, self.unknownFloat1b, self.unknownFloat1c, self.unknownFloat1d, self.particleSizes1.toBytes(), self.rotationValues1.toBytes(), self.initialColor1.toBytes(), self.finalColor1.toBytes(), self.unknownColor1.toBytes(), self.slowdown, self.unknownFloat2a, self.unknownFloat2b, self.unknownFloat2c, self.unknown4, self.trailingEnabled, self.unknown5, self.unknown6, self.unknownFloat3a, self.unknownFloat3b, self.unknownFloat3c, self.unknownFloat3d, self.indexPlusHighestIndex, self.maxParticles, self.emissionRate.toBytes(), self.emissionAreaType, self.emissionAreaSize.toBytes(), self.tailUnk1.toBytes(), self.emissionAreaRadius.toBytes(), self.spreadUnk.toBytes(), self.emissionType, self.randomizeWithParticleSizes2, self.particleSizes2.toBytes(), self.randomizeWithRotationValues2, self.rotationValues2.toBytes(), self.randomizeWithColor2, self.initialColor2.toBytes(), self.finalColor2.toBytes(), self.unknownColor2.toBytes(), self.unknown7, self.partEmit.toBytes(), self.phase1StartImageIndex, self.phase1EndImageIndex, self.phase2EndImageIndex, self.phase2StartImageIndex, self.relativePhase1Length, self.numberOfColumns, self.numberOfRows, self.columnWidth, self.rowHeight, self.unknownFloat4, self.unknownFloat5, self.unknown9, self.unknown10, self.unknownFloat6, self.unknown11, self.unknownFloat7, self.unknown12, self.flags, self.unknown13, self.ar1.toBytes(), self.unknown14, self.copyIndices.toBytes())
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(PAR_V12.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = PAR_V12.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += PAR_V12.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return PAR_V12.countOneOrMore(object) * PAR_V12.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"emissionAreaRadius": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "emissionRate": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "emissionSpreadY": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "emissionSpreadX": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "materialReferenceIndex": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "lifespan2": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "lifespan1": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "rowHeight": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "slowdown": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "unknownFloat5": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "unknownColor1": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "unknownColor2": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "spreadUnk": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "unknownFloat6": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "emissionAreaSize": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "particleSizes2": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "randomizeWithLifespan2": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "particleSizes1": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "trailingEnabled": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "unknownFloat2a": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "unknownFloat2b": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "unknownFloat2c": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "emissionAreaType": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "emissionType": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "unknownFloat4": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "numberOfColumns": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "randomizeWithColor2": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "unknownFloat1c": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "unknown2": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "randomizeWithParticleSizes2": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "unknown0": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "unknown1": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "unknown6": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "unknown7": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "unknown4": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "unknown5": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "unknown9": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "ar1": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "rotationValues2": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "rotationValues1": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "partEmit": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "phase2EndImageIndex": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "indexPlusHighestIndex": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "unknown10": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "unknown11": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "unknown12": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "unknown13": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "unknown14": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "relativePhase1Length": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "tailUnk1": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "finalColor1": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "finalColor2": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "zAcceleration": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "initialColor2": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "randomizeWithEmissionSpeed2": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "phase2StartImageIndex": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "copyIndices": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "unknownFloat1d": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "unknownFloat1a": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "emissionSpeed1": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "emissionSpeed2": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "unknownFloat1b": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "randomizeWithRotationValues2": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "columnWidth": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "initialColor1": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "unknownFloat7": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "numberOfRows": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "emissionAngleX": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "emissionAngleY": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "phase1StartImageIndex": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "phase1EndImageIndex": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "flags": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "unknownFloat3a": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "unknownFloat3d": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "unknownFloat3c": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "unknownFloat3b": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "bone": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}, "maxParticles": {"simulateOnInit":0x4000000, "inheritParentVel":0x40, "spawnOnBounce":0x8, "sortByZHeight":0x80, "bezSmoothSize":0x1000, "smoothRotation":0x200, "inheritEmissionParams":0x20, "useLocalTime":0x2000000, "multiplyByGravity":0x20000, "randFlipBookStart":0x10000, "copy":0x8000000, "bezSmoothColor":0x4000, "clampTailParts":0x40000, "scaleTimeByParent":0x1000000, "bezSmoothRotation":0x400, "spawnTrailingParts":0x80000, "sort":0x1, "fixLengthTailParts":0x100000, "useVertexAlpha":0x200000, "collideObjects":0x4, "reverseIteration":0x100, "litParts":0x8000, "modelParts":0x400000, "collideTerrain":0x2, "smoothColor":0x2000, "useInnerShape":0x10, "swapYZonModelParts":0x800000, "smoothSize":0x800}}
    
    def getNamedBit(self, field, bitName):
        mask = PAR_V12.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = PAR_V12.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return PAR_V12.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"bone":FieldTypeInfo("uint32",None, False), "materialReferenceIndex":FieldTypeInfo("uint32",None, False), "emissionSpeed1":FieldTypeInfo("FloatAnimationReference",FloatAnimationReference, False), "emissionSpeed2":FieldTypeInfo("FloatAnimationReference",FloatAnimationReference, False), "randomizeWithEmissionSpeed2":FieldTypeInfo("uint32",None, False), "emissionAngleX":FieldTypeInfo("FloatAnimationReference",FloatAnimationReference, False), "emissionAngleY":FieldTypeInfo("FloatAnimationReference",FloatAnimationReference, False), "emissionSpreadX":FieldTypeInfo("FloatAnimationReference",FloatAnimationReference, False), "emissionSpreadY":FieldTypeInfo("FloatAnimationReference",FloatAnimationReference, False), "lifespan1":FieldTypeInfo("FloatAnimationReference",FloatAnimationReference, False), "lifespan2":FieldTypeInfo("FloatAnimationReference",FloatAnimationReference, False), "randomizeWithLifespan2":FieldTypeInfo("uint32",None, False), "unknown0":FieldTypeInfo("uint32",None, False), "unknown1":FieldTypeInfo("uint32",None, False), "unknown2":FieldTypeInfo("uint32",None, False), "zAcceleration":FieldTypeInfo("float",None, False), "unknownFloat1a":FieldTypeInfo("float",None, False), "unknownFloat1b":FieldTypeInfo("float",None, False), "unknownFloat1c":FieldTypeInfo("float",None, False), "unknownFloat1d":FieldTypeInfo("float",None, False), "particleSizes1":FieldTypeInfo("Vector3AnimationReference",Vector3AnimationReference, False), "rotationValues1":FieldTypeInfo("Vector3AnimationReference",Vector3AnimationReference, False), "initialColor1":FieldTypeInfo("ColorAnimationReference",ColorAnimationReference, False), "finalColor1":FieldTypeInfo("ColorAnimationReference",ColorAnimationReference, False), "unknownColor1":FieldTypeInfo("ColorAnimationReference",ColorAnimationReference, False), "slowdown":FieldTypeInfo("float",None, False), "unknownFloat2a":FieldTypeInfo("float",None, False), "unknownFloat2b":FieldTypeInfo("float",None, False), "unknownFloat2c":FieldTypeInfo("float",None, False), "unknown4":FieldTypeInfo("float",None, False), "trailingEnabled":FieldTypeInfo("uint32",None, False), "unknown5":FieldTypeInfo("uint32",None, False), "unknown6":FieldTypeInfo("uint32",None, False), "unknownFloat3a":FieldTypeInfo("float",None, False), "unknownFloat3b":FieldTypeInfo("float",None, False), "unknownFloat3c":FieldTypeInfo("float",None, False), "unknownFloat3d":FieldTypeInfo("float",None, False), "indexPlusHighestIndex":FieldTypeInfo("uint32",None, False), "maxParticles":FieldTypeInfo("uint32",None, False), "emissionRate":FieldTypeInfo("FloatAnimationReference",FloatAnimationReference, False), "emissionAreaType":FieldTypeInfo("uint32",None, False), "emissionAreaSize":FieldTypeInfo("Vector3AnimationReference",Vector3AnimationReference, False), "tailUnk1":FieldTypeInfo("Vector3AnimationReference",Vector3AnimationReference, False), "emissionAreaRadius":FieldTypeInfo("FloatAnimationReference",FloatAnimationReference, False), "spreadUnk":FieldTypeInfo("FloatAnimationReference",FloatAnimationReference, False), "emissionType":FieldTypeInfo("uint32",None, False), "randomizeWithParticleSizes2":FieldTypeInfo("uint32",None, False), "particleSizes2":FieldTypeInfo("Vector3AnimationReference",Vector3AnimationReference, False), "randomizeWithRotationValues2":FieldTypeInfo("uint32",None, False), "rotationValues2":FieldTypeInfo("Vector3AnimationReference",Vector3AnimationReference, False), "randomizeWithColor2":FieldTypeInfo("uint32",None, False), "initialColor2":FieldTypeInfo("ColorAnimationReference",ColorAnimationReference, False), "finalColor2":FieldTypeInfo("ColorAnimationReference",ColorAnimationReference, False), "unknownColor2":FieldTypeInfo("ColorAnimationReference",ColorAnimationReference, False), "unknown7":FieldTypeInfo("uint32",None, False), "partEmit":FieldTypeInfo("Int16AnimationReference",Int16AnimationReference, False), "phase1StartImageIndex":FieldTypeInfo("uint8",None, False), "phase1EndImageIndex":FieldTypeInfo("uint8",None, False), "phase2EndImageIndex":FieldTypeInfo("uint8",None, False), "phase2StartImageIndex":FieldTypeInfo("uint8",None, False), "relativePhase1Length":FieldTypeInfo("float",None, False), "numberOfColumns":FieldTypeInfo("uint16",None, False), "numberOfRows":FieldTypeInfo("uint16",None, False), "columnWidth":FieldTypeInfo("float",None, False), "rowHeight":FieldTypeInfo("float",None, False), "unknownFloat4":FieldTypeInfo("float",None, False), "unknownFloat5":FieldTypeInfo("float",None, False), "unknown9":FieldTypeInfo("int32",None, False), "unknown10":FieldTypeInfo(None,None, False), "unknownFloat6":FieldTypeInfo("float",None, False), "unknown11":FieldTypeInfo(None,None, False), "unknownFloat7":FieldTypeInfo("float",None, False), "unknown12":FieldTypeInfo(None,None, False), "flags":FieldTypeInfo("uint32",None, False), "unknown13":FieldTypeInfo(None,None, False), "ar1":FieldTypeInfo("FloatAnimationReference",FloatAnimationReference, False), "unknown14":FieldTypeInfo(None,None, False), "copyIndices":FieldTypeInfo("U32_V0",U32_V0, True)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return PAR_V12.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != PAR_V12:
            raise Exception("%s is not of type %s but %s" % (id, "PAR_V12", type(instance)))
        fieldId = id + ".bone"

        if (type(instance.bone) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".materialReferenceIndex"

        if (type(instance.materialReferenceIndex) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".emissionSpeed1"

        FloatAnimationReference.validateInstance(instance.emissionSpeed1, fieldId)
        fieldId = id + ".emissionSpeed2"

        FloatAnimationReference.validateInstance(instance.emissionSpeed2, fieldId)
        fieldId = id + ".randomizeWithEmissionSpeed2"

        if (type(instance.randomizeWithEmissionSpeed2) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".emissionAngleX"

        FloatAnimationReference.validateInstance(instance.emissionAngleX, fieldId)
        fieldId = id + ".emissionAngleY"

        FloatAnimationReference.validateInstance(instance.emissionAngleY, fieldId)
        fieldId = id + ".emissionSpreadX"

        FloatAnimationReference.validateInstance(instance.emissionSpreadX, fieldId)
        fieldId = id + ".emissionSpreadY"

        FloatAnimationReference.validateInstance(instance.emissionSpreadY, fieldId)
        fieldId = id + ".lifespan1"

        FloatAnimationReference.validateInstance(instance.lifespan1, fieldId)
        fieldId = id + ".lifespan2"

        FloatAnimationReference.validateInstance(instance.lifespan2, fieldId)
        fieldId = id + ".randomizeWithLifespan2"

        if (type(instance.randomizeWithLifespan2) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".unknown0"

        if (type(instance.unknown0) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".unknown1"

        if (type(instance.unknown1) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".unknown2"

        if (type(instance.unknown2) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".zAcceleration"

        if (type(instance.zAcceleration) != float):
            raise Exception("%s is not a float" % (fieldId))
        fieldId = id + ".unknownFloat1a"

        if (type(instance.unknownFloat1a) != float):
            raise Exception("%s is not a float" % (fieldId))
        fieldId = id + ".unknownFloat1b"

        if (type(instance.unknownFloat1b) != float):
            raise Exception("%s is not a float" % (fieldId))
        fieldId = id + ".unknownFloat1c"

        if (type(instance.unknownFloat1c) != float):
            raise Exception("%s is not a float" % (fieldId))
        fieldId = id + ".unknownFloat1d"

        if (type(instance.unknownFloat1d) != float):
            raise Exception("%s is not a float" % (fieldId))
        fieldId = id + ".particleSizes1"

        Vector3AnimationReference.validateInstance(instance.particleSizes1, fieldId)
        fieldId = id + ".rotationValues1"

        Vector3AnimationReference.validateInstance(instance.rotationValues1, fieldId)
        fieldId = id + ".initialColor1"

        ColorAnimationReference.validateInstance(instance.initialColor1, fieldId)
        fieldId = id + ".finalColor1"

        ColorAnimationReference.validateInstance(instance.finalColor1, fieldId)
        fieldId = id + ".unknownColor1"

        ColorAnimationReference.validateInstance(instance.unknownColor1, fieldId)
        fieldId = id + ".slowdown"

        if (type(instance.slowdown) != float):
            raise Exception("%s is not a float" % (fieldId))
        fieldId = id + ".unknownFloat2a"

        if (type(instance.unknownFloat2a) != float):
            raise Exception("%s is not a float" % (fieldId))
        fieldId = id + ".unknownFloat2b"

        if (type(instance.unknownFloat2b) != float):
            raise Exception("%s is not a float" % (fieldId))
        fieldId = id + ".unknownFloat2c"

        if (type(instance.unknownFloat2c) != float):
            raise Exception("%s is not a float" % (fieldId))
        fieldId = id + ".unknown4"

        if (type(instance.unknown4) != float):
            raise Exception("%s is not a float" % (fieldId))
        fieldId = id + ".trailingEnabled"

        if (type(instance.trailingEnabled) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".unknown5"

        if (type(instance.unknown5) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".unknown6"

        if (type(instance.unknown6) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".unknownFloat3a"

        if (type(instance.unknownFloat3a) != float):
            raise Exception("%s is not a float" % (fieldId))
        fieldId = id + ".unknownFloat3b"

        if (type(instance.unknownFloat3b) != float):
            raise Exception("%s is not a float" % (fieldId))
        fieldId = id + ".unknownFloat3c"

        if (type(instance.unknownFloat3c) != float):
            raise Exception("%s is not a float" % (fieldId))
        fieldId = id + ".unknownFloat3d"

        if (type(instance.unknownFloat3d) != float):
            raise Exception("%s is not a float" % (fieldId))
        fieldId = id + ".indexPlusHighestIndex"

        if (type(instance.indexPlusHighestIndex) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".maxParticles"

        if (type(instance.maxParticles) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".emissionRate"

        FloatAnimationReference.validateInstance(instance.emissionRate, fieldId)
        fieldId = id + ".emissionAreaType"

        if (type(instance.emissionAreaType) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".emissionAreaSize"

        Vector3AnimationReference.validateInstance(instance.emissionAreaSize, fieldId)
        fieldId = id + ".tailUnk1"

        Vector3AnimationReference.validateInstance(instance.tailUnk1, fieldId)
        fieldId = id + ".emissionAreaRadius"

        FloatAnimationReference.validateInstance(instance.emissionAreaRadius, fieldId)
        fieldId = id + ".spreadUnk"

        FloatAnimationReference.validateInstance(instance.spreadUnk, fieldId)
        fieldId = id + ".emissionType"

        if (type(instance.emissionType) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".randomizeWithParticleSizes2"

        if (type(instance.randomizeWithParticleSizes2) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".particleSizes2"

        Vector3AnimationReference.validateInstance(instance.particleSizes2, fieldId)
        fieldId = id + ".randomizeWithRotationValues2"

        if (type(instance.randomizeWithRotationValues2) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".rotationValues2"

        Vector3AnimationReference.validateInstance(instance.rotationValues2, fieldId)
        fieldId = id + ".randomizeWithColor2"

        if (type(instance.randomizeWithColor2) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".initialColor2"

        ColorAnimationReference.validateInstance(instance.initialColor2, fieldId)
        fieldId = id + ".finalColor2"

        ColorAnimationReference.validateInstance(instance.finalColor2, fieldId)
        fieldId = id + ".unknownColor2"

        ColorAnimationReference.validateInstance(instance.unknownColor2, fieldId)
        fieldId = id + ".unknown7"

        if (type(instance.unknown7) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".partEmit"

        Int16AnimationReference.validateInstance(instance.partEmit, fieldId)
        fieldId = id + ".phase1StartImageIndex"

        if (type(instance.phase1StartImageIndex) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".phase1EndImageIndex"

        if (type(instance.phase1EndImageIndex) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".phase2EndImageIndex"

        if (type(instance.phase2EndImageIndex) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".phase2StartImageIndex"

        if (type(instance.phase2StartImageIndex) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".relativePhase1Length"

        if (type(instance.relativePhase1Length) != float):
            raise Exception("%s is not a float" % (fieldId))
        fieldId = id + ".numberOfColumns"

        if (type(instance.numberOfColumns) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".numberOfRows"

        if (type(instance.numberOfRows) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".columnWidth"

        if (type(instance.columnWidth) != float):
            raise Exception("%s is not a float" % (fieldId))
        fieldId = id + ".rowHeight"

        if (type(instance.rowHeight) != float):
            raise Exception("%s is not a float" % (fieldId))
        fieldId = id + ".unknownFloat4"

        if (type(instance.unknownFloat4) != float):
            raise Exception("%s is not a float" % (fieldId))
        fieldId = id + ".unknownFloat5"

        if (type(instance.unknownFloat5) != float):
            raise Exception("%s is not a float" % (fieldId))
        fieldId = id + ".unknown9"

        if (type(instance.unknown9) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".unknown10"

        if (type(instance.unknown10) != bytes) or (len(instance.unknown10) != 24):
            raise Exception("%s is not an bytes object of size %s" % (fieldId, "24"))
        fieldId = id + ".unknownFloat6"

        if (type(instance.unknownFloat6) != float):
            raise Exception("%s is not a float" % (fieldId))
        fieldId = id + ".unknown11"

        if (type(instance.unknown11) != bytes) or (len(instance.unknown11) != 8):
            raise Exception("%s is not an bytes object of size %s" % (fieldId, "8"))
        fieldId = id + ".unknownFloat7"

        if (type(instance.unknownFloat7) != float):
            raise Exception("%s is not a float" % (fieldId))
        fieldId = id + ".unknown12"

        if (type(instance.unknown12) != bytes) or (len(instance.unknown12) != 416):
            raise Exception("%s is not an bytes object of size %s" % (fieldId, "416"))
        fieldId = id + ".flags"

        if (type(instance.flags) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".unknown13"

        if (type(instance.unknown13) != bytes) or (len(instance.unknown13) != 44):
            raise Exception("%s is not an bytes object of size %s" % (fieldId, "44"))
        fieldId = id + ".ar1"

        FloatAnimationReference.validateInstance(instance.ar1, fieldId)
        fieldId = id + ".unknown14"

        if (type(instance.unknown14) != bytes) or (len(instance.unknown14) != 48):
            raise Exception("%s is not an bytes object of size %s" % (fieldId, "48"))
        fieldId = id + ".copyIndices"
        if (type(instance.copyIndices) != list):
            raise Exception("%s is not a list of integers" % (fieldId))
        for itemIndex, item in enumerate(instance.copyIndices):
            itemId = "%s[%d]" % (fieldId, itemIndex)
            if type(item) != int: 
                raise Exception("%s is not an integer" % (itemId))
            if (item < 0) or (item > 8589934591):
                raise Exception("%s has value %d which is not in range [0, 8589934591]"  % (itemId, item))


class PARCV0:
    """
                Particle System Copy/Instance
            """
    fullName = "PARCV0"
    tagName = "PARC"
    tagVersion = 0
    size = 40
    structFormat = struct.Struct("<20s16sI")
    fields = ["emissionRate", "partEmit", "bone"]

    def __setattr__(self, name, value):
        if name in ["emissionRate", "partEmit", "bone"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["emissionRate", "partEmit", "bone"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        pass #nothing to do
    
    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        pass #nothing to do

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert PARCV0.size == PARCV0.structFormat.size
            rawBytes = readable.read(PARCV0.size)
        if rawBytes != None:
            l = PARCV0.structFormat.unpack(rawBytes)
            self.emissionRate = FloatAnimationReference(rawBytes=l[0])
            self.partEmit = Int16AnimationReference(rawBytes=l[1])
            self.bone = l[2]
        if (readable == None) and (rawBytes == None):
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + PARCV0.size
        for i in range(count):
            list.append(PARCV0(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += PARCV0.size
        return list
    
    def toBytes(self):
        return PARCV0.structFormat.pack(self.emissionRate.toBytes(), self.partEmit.toBytes(), self.bone)
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(PARCV0.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = PARCV0.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += PARCV0.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return PARCV0.countOneOrMore(object) * PARCV0.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"emissionRate": {}, "bone": {}, "partEmit": {}}
    
    def getNamedBit(self, field, bitName):
        mask = PARCV0.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = PARCV0.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return PARCV0.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"emissionRate":FieldTypeInfo("FloatAnimationReference",FloatAnimationReference, False), "partEmit":FieldTypeInfo("Int16AnimationReference",Int16AnimationReference, False), "bone":FieldTypeInfo("uint32",None, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return PARCV0.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != PARCV0:
            raise Exception("%s is not of type %s but %s" % (id, "PARCV0", type(instance)))
        fieldId = id + ".emissionRate"

        FloatAnimationReference.validateInstance(instance.emissionRate, fieldId)
        fieldId = id + ".partEmit"

        Int16AnimationReference.validateInstance(instance.partEmit, fieldId)
        fieldId = id + ".bone"

        if (type(instance.bone) != int):
            raise Exception("%s is not an int" % (fieldId))


class PROJV4:
    """"""
    fullName = "PROJV4"
    tagName = "PROJ"
    tagVersion = 4
    size = 388
    structFormat = struct.Struct("<388s")
    fields = ["unknown"]

    def __setattr__(self, name, value):
        if name in ["unknown"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["unknown"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        pass #nothing to do
    
    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        pass #nothing to do

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert PROJV4.size == PROJV4.structFormat.size
            rawBytes = readable.read(PROJV4.size)
        if rawBytes != None:
            l = PROJV4.structFormat.unpack(rawBytes)
            self.unknown = l[0]
        if (readable == None) and (rawBytes == None):
            self.unknown = bytes(388)
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + PROJV4.size
        for i in range(count):
            list.append(PROJV4(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += PROJV4.size
        return list
    
    def toBytes(self):
        return PROJV4.structFormat.pack(self.unknown)
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(PROJV4.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = PROJV4.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += PROJV4.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return PROJV4.countOneOrMore(object) * PROJV4.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"unknown": {}}
    
    def getNamedBit(self, field, bitName):
        mask = PROJV4.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = PROJV4.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return PROJV4.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"unknown":FieldTypeInfo(None,None, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return PROJV4.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != PROJV4:
            raise Exception("%s is not of type %s but %s" % (id, "PROJV4", type(instance)))
        fieldId = id + ".unknown"

        if (type(instance.unknown) != bytes) or (len(instance.unknown) != 388):
            raise Exception("%s is not an bytes object of size %s" % (fieldId, "388"))


class FOR_V1:
    """
                Unknown
            """
    fullName = "FOR_V1"
    tagName = "FOR_"
    tagVersion = 1
    size = 104
    structFormat = struct.Struct("<104s")
    fields = ["unknown"]

    def __setattr__(self, name, value):
        if name in ["unknown"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["unknown"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        pass #nothing to do
    
    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        pass #nothing to do

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert FOR_V1.size == FOR_V1.structFormat.size
            rawBytes = readable.read(FOR_V1.size)
        if rawBytes != None:
            l = FOR_V1.structFormat.unpack(rawBytes)
            self.unknown = l[0]
        if (readable == None) and (rawBytes == None):
            self.unknown = bytes(104)
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + FOR_V1.size
        for i in range(count):
            list.append(FOR_V1(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += FOR_V1.size
        return list
    
    def toBytes(self):
        return FOR_V1.structFormat.pack(self.unknown)
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(FOR_V1.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = FOR_V1.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += FOR_V1.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return FOR_V1.countOneOrMore(object) * FOR_V1.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"unknown": {}}
    
    def getNamedBit(self, field, bitName):
        mask = FOR_V1.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = FOR_V1.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return FOR_V1.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"unknown":FieldTypeInfo(None,None, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return FOR_V1.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != FOR_V1:
            raise Exception("%s is not of type %s but %s" % (id, "FOR_V1", type(instance)))
        fieldId = id + ".unknown"

        if (type(instance.unknown) != bytes) or (len(instance.unknown) != 104):
            raise Exception("%s is not an bytes object of size %s" % (fieldId, "104"))


class PHSHV1:
    """"""
    fullName = "PHSHV1"
    tagName = "PHSH"
    tagVersion = 1
    size = 132
    structFormat = struct.Struct("<72s8s16s8s4s8s16s")
    fields = ["unknown0", "unknown1", "unknown2", "unknown3", "unknown4", "unknown5", "unknown6"]

    def __setattr__(self, name, value):
        if name in ["unknown0", "unknown1", "unknown2", "unknown3", "unknown4", "unknown5", "unknown6"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["unknown0", "unknown1", "unknown2", "unknown3", "unknown4", "unknown5", "unknown6"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    def resolveReferences(self, sections):
        self.unknown1 = resolveRef(self.unknown1,sections,VEC3V0,"PHSHV1.unknown1")
        self.unknown3 = resolveRef(self.unknown3,sections,U16_V0,"PHSHV1.unknown3")
        self.unknown5 = resolveRef(self.unknown5,sections,VEC4V0,"PHSHV1.unknown5")


    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        if oneOrMore.__class__ == [].__class__:
            for object in oneOrMore:
                object.resolveReferences(sections) 
        else:
            oneOrMore.resolveReferences(sections)

    def introduceIndexReferences(self, indexMaker):
        indexReference = indexMaker.getIndexReferenceTo(self.unknown1, SmallReference, VEC3V0)
        VEC3V0.introduceIndexReferencesForOneOrMore(self.unknown1,  indexMaker)
        self.unknown1 = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.unknown3, SmallReference, U16_V0)
        U16_V0.introduceIndexReferencesForOneOrMore(self.unknown3,  indexMaker)
        self.unknown3 = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.unknown5, SmallReference, VEC4V0)
        VEC4V0.introduceIndexReferencesForOneOrMore(self.unknown5,  indexMaker)
        self.unknown5 = indexReference


    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        if object.__class__ == MD34IndexEntry:
            return # nothing to do (object was reachable trough 2 paths)
        if object.__class__ == [].__class__:
            for o in object:
                o.introduceIndexReferences(indexMaker) 
        else:
            object.introduceIndexReferences(indexMaker)

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert PHSHV1.size == PHSHV1.structFormat.size
            rawBytes = readable.read(PHSHV1.size)
        if rawBytes != None:
            l = PHSHV1.structFormat.unpack(rawBytes)
            self.unknown0 = l[0]
            self.unknown1 = SmallReference(rawBytes=l[1])
            self.unknown2 = l[2]
            self.unknown3 = SmallReference(rawBytes=l[3])
            self.unknown4 = l[4]
            self.unknown5 = SmallReference(rawBytes=l[5])
            self.unknown6 = l[6]
        if (readable == None) and (rawBytes == None):
            self.unknown0 = bytes(72)
            self.unknown1 = VEC3V0.createEmptyArray()
            self.unknown2 = bytes(16)
            self.unknown3 = U16_V0.createEmptyArray()
            self.unknown4 = bytes(4)
            self.unknown5 = VEC4V0.createEmptyArray()
            self.unknown6 = bytes(16)
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + PHSHV1.size
        for i in range(count):
            list.append(PHSHV1(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += PHSHV1.size
        return list
    
    def toBytes(self):
        return PHSHV1.structFormat.pack(self.unknown0, self.unknown1.toBytes(), self.unknown2, self.unknown3.toBytes(), self.unknown4, self.unknown5.toBytes(), self.unknown6)
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(PHSHV1.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = PHSHV1.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += PHSHV1.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return PHSHV1.countOneOrMore(object) * PHSHV1.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"unknown2": {}, "unknown3": {}, "unknown0": {}, "unknown1": {}, "unknown6": {}, "unknown4": {}, "unknown5": {}}
    
    def getNamedBit(self, field, bitName):
        mask = PHSHV1.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = PHSHV1.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return PHSHV1.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"unknown0":FieldTypeInfo(None,None, False), "unknown1":FieldTypeInfo("VEC3V0",VEC3V0, True), "unknown2":FieldTypeInfo(None,None, False), "unknown3":FieldTypeInfo("U16_V0",U16_V0, True), "unknown4":FieldTypeInfo(None,None, False), "unknown5":FieldTypeInfo("VEC4V0",VEC4V0, True), "unknown6":FieldTypeInfo(None,None, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return PHSHV1.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != PHSHV1:
            raise Exception("%s is not of type %s but %s" % (id, "PHSHV1", type(instance)))
        fieldId = id + ".unknown0"

        if (type(instance.unknown0) != bytes) or (len(instance.unknown0) != 72):
            raise Exception("%s is not an bytes object of size %s" % (fieldId, "72"))
        fieldId = id + ".unknown1"

        if (type(instance.unknown1) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "VEC3V0", type(instance.unknown1)))
        for itemIndex, item in enumerate(instance.unknown1):
            VEC3V0.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".unknown2"

        if (type(instance.unknown2) != bytes) or (len(instance.unknown2) != 16):
            raise Exception("%s is not an bytes object of size %s" % (fieldId, "16"))
        fieldId = id + ".unknown3"
        if (type(instance.unknown3) != list):
            raise Exception("%s is not a list of integers" % (fieldId))
        for itemIndex, item in enumerate(instance.unknown3):
            itemId = "%s[%d]" % (fieldId, itemIndex)
            if type(item) != int: 
                raise Exception("%s is not an integer" % (itemId))
            if (item < 0) or (item > 131071):
                raise Exception("%s has value %d which is not in range [0, 131071]"  % (itemId, item))
        fieldId = id + ".unknown4"

        if (type(instance.unknown4) != bytes) or (len(instance.unknown4) != 4):
            raise Exception("%s is not an bytes object of size %s" % (fieldId, "4"))
        fieldId = id + ".unknown5"

        if (type(instance.unknown5) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "VEC4V0", type(instance.unknown5)))
        for itemIndex, item in enumerate(instance.unknown5):
            VEC4V0.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".unknown6"

        if (type(instance.unknown6) != bytes) or (len(instance.unknown6) != 16):
            raise Exception("%s is not an bytes object of size %s" % (fieldId, "16"))


class PHRBV2:
    """"""
    fullName = "PHRBV2"
    tagName = "PHRB"
    tagVersion = 2
    size = 104
    structFormat = struct.Struct("<80s12s12s")
    fields = ["unknown0", "phshData", "unknown1"]

    def __setattr__(self, name, value):
        if name in ["unknown0", "phshData", "unknown1"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["unknown0", "phshData", "unknown1"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    def resolveReferences(self, sections):
        self.phshData = resolveRef(self.phshData,sections,PHSHV1,"PHRBV2.phshData")


    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        if oneOrMore.__class__ == [].__class__:
            for object in oneOrMore:
                object.resolveReferences(sections) 
        else:
            oneOrMore.resolveReferences(sections)

    def introduceIndexReferences(self, indexMaker):
        indexReference = indexMaker.getIndexReferenceTo(self.phshData, Reference, PHSHV1)
        PHSHV1.introduceIndexReferencesForOneOrMore(self.phshData,  indexMaker)
        self.phshData = indexReference


    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        if object.__class__ == MD34IndexEntry:
            return # nothing to do (object was reachable trough 2 paths)
        if object.__class__ == [].__class__:
            for o in object:
                o.introduceIndexReferences(indexMaker) 
        else:
            object.introduceIndexReferences(indexMaker)

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert PHRBV2.size == PHRBV2.structFormat.size
            rawBytes = readable.read(PHRBV2.size)
        if rawBytes != None:
            l = PHRBV2.structFormat.unpack(rawBytes)
            self.unknown0 = l[0]
            self.phshData = Reference(rawBytes=l[1])
            self.unknown1 = l[2]
        if (readable == None) and (rawBytes == None):
            self.unknown0 = bytes(80)
            self.phshData = PHSHV1.createEmptyArray()
            self.unknown1 = bytes(12)
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + PHRBV2.size
        for i in range(count):
            list.append(PHRBV2(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += PHRBV2.size
        return list
    
    def toBytes(self):
        return PHRBV2.structFormat.pack(self.unknown0, self.phshData.toBytes(), self.unknown1)
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(PHRBV2.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = PHRBV2.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += PHRBV2.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return PHRBV2.countOneOrMore(object) * PHRBV2.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"phshData": {}, "unknown0": {}, "unknown1": {}}
    
    def getNamedBit(self, field, bitName):
        mask = PHRBV2.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = PHRBV2.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return PHRBV2.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"unknown0":FieldTypeInfo(None,None, False), "phshData":FieldTypeInfo("PHSHV1",PHSHV1, True), "unknown1":FieldTypeInfo(None,None, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return PHRBV2.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != PHRBV2:
            raise Exception("%s is not of type %s but %s" % (id, "PHRBV2", type(instance)))
        fieldId = id + ".unknown0"

        if (type(instance.unknown0) != bytes) or (len(instance.unknown0) != 80):
            raise Exception("%s is not an bytes object of size %s" % (fieldId, "80"))
        fieldId = id + ".phshData"

        if (type(instance.phshData) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "PHSHV1", type(instance.phshData)))
        for itemIndex, item in enumerate(instance.phshData):
            PHSHV1.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".unknown1"

        if (type(instance.unknown1) != bytes) or (len(instance.unknown1) != 12):
            raise Exception("%s is not an bytes object of size %s" % (fieldId, "12"))


class SSGSV1:
    """
                Unknown
            """
    fullName = "SSGSV1"
    tagName = "SSGS"
    tagVersion = 1
    size = 108
    structFormat = struct.Struct("<108s")
    fields = ["unknown"]

    def __setattr__(self, name, value):
        if name in ["unknown"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["unknown"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        pass #nothing to do
    
    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        pass #nothing to do

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert SSGSV1.size == SSGSV1.structFormat.size
            rawBytes = readable.read(SSGSV1.size)
        if rawBytes != None:
            l = SSGSV1.structFormat.unpack(rawBytes)
            self.unknown = l[0]
        if (readable == None) and (rawBytes == None):
            self.unknown = bytes(108)
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + SSGSV1.size
        for i in range(count):
            list.append(SSGSV1(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += SSGSV1.size
        return list
    
    def toBytes(self):
        return SSGSV1.structFormat.pack(self.unknown)
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(SSGSV1.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = SSGSV1.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += SSGSV1.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return SSGSV1.countOneOrMore(object) * SSGSV1.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"unknown": {}}
    
    def getNamedBit(self, field, bitName):
        mask = SSGSV1.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = SSGSV1.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return SSGSV1.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"unknown":FieldTypeInfo(None,None, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return SSGSV1.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != SSGSV1:
            raise Exception("%s is not of type %s but %s" % (id, "SSGSV1", type(instance)))
        fieldId = id + ".unknown"

        if (type(instance.unknown) != bytes) or (len(instance.unknown) != 108):
            raise Exception("%s is not an bytes object of size %s" % (fieldId, "108"))


class ATVLV0:
    """
                Attachment Volume
                
                The type attribute specifies the meaning of the size values:
                
                0 = Cuboid (width=size0, length=size1, height=size2)
                1 = Sphere (radius=size0)
                2 = Cylinder (radius=size0, height=size1)) 
            """
    fullName = "ATVLV0"
    tagName = "ATVL"
    tagVersion = 0
    size = 116
    structFormat = struct.Struct("<IIII64s12s12sfff")
    fields = ["bone0", "bone1", "type", "bone2", "matrix", "unknown0", "unknown1", "size0", "size1", "size2"]

    def __setattr__(self, name, value):
        if name in ["bone0", "bone1", "type", "bone2", "matrix", "unknown0", "unknown1", "size0", "size1", "size2"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["bone0", "bone1", "type", "bone2", "matrix", "unknown0", "unknown1", "size0", "size1", "size2"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    def resolveReferences(self, sections):
        self.unknown0 = resolveRef(self.unknown0,sections,VEC3V0,"ATVLV0.unknown0")
        self.unknown1 = resolveRef(self.unknown1,sections,U16_V0,"ATVLV0.unknown1")


    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        if oneOrMore.__class__ == [].__class__:
            for object in oneOrMore:
                object.resolveReferences(sections) 
        else:
            oneOrMore.resolveReferences(sections)

    def introduceIndexReferences(self, indexMaker):
        indexReference = indexMaker.getIndexReferenceTo(self.unknown0, Reference, VEC3V0)
        VEC3V0.introduceIndexReferencesForOneOrMore(self.unknown0,  indexMaker)
        self.unknown0 = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.unknown1, Reference, U16_V0)
        U16_V0.introduceIndexReferencesForOneOrMore(self.unknown1,  indexMaker)
        self.unknown1 = indexReference


    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        if object.__class__ == MD34IndexEntry:
            return # nothing to do (object was reachable trough 2 paths)
        if object.__class__ == [].__class__:
            for o in object:
                o.introduceIndexReferences(indexMaker) 
        else:
            object.introduceIndexReferences(indexMaker)

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert ATVLV0.size == ATVLV0.structFormat.size
            rawBytes = readable.read(ATVLV0.size)
        if rawBytes != None:
            l = ATVLV0.structFormat.unpack(rawBytes)
            self.bone0 = l[0]
            self.bone1 = l[1]
            self.type = l[2]
            self.bone2 = l[3]
            self.matrix = Matrix44(rawBytes=l[4])
            self.unknown0 = Reference(rawBytes=l[5])
            self.unknown1 = Reference(rawBytes=l[6])
            self.size0 = l[7]
            self.size1 = l[8]
            self.size2 = l[9]
        if (readable == None) and (rawBytes == None):
            self.type = 1
            self.unknown0 = VEC3V0.createEmptyArray()
            self.unknown1 = U16_V0.createEmptyArray()
            self.size1 = 0.0
            self.size2 = 0.0
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + ATVLV0.size
        for i in range(count):
            list.append(ATVLV0(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += ATVLV0.size
        return list
    
    def toBytes(self):
        return ATVLV0.structFormat.pack(self.bone0, self.bone1, self.type, self.bone2, self.matrix.toBytes(), self.unknown0.toBytes(), self.unknown1.toBytes(), self.size0, self.size1, self.size2)
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(ATVLV0.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = ATVLV0.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += ATVLV0.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return ATVLV0.countOneOrMore(object) * ATVLV0.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"size0": {}, "matrix": {}, "size2": {}, "unknown0": {}, "unknown1": {}, "bone2": {}, "bone1": {}, "bone0": {}, "type": {}, "size1": {}}
    
    def getNamedBit(self, field, bitName):
        mask = ATVLV0.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = ATVLV0.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return ATVLV0.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"bone0":FieldTypeInfo("uint32",None, False), "bone1":FieldTypeInfo("uint32",None, False), "type":FieldTypeInfo("uint32",None, False), "bone2":FieldTypeInfo("uint32",None, False), "matrix":FieldTypeInfo("Matrix44",Matrix44, False), "unknown0":FieldTypeInfo("VEC3V0",VEC3V0, True), "unknown1":FieldTypeInfo("U16_V0",U16_V0, True), "size0":FieldTypeInfo("float",None, False), "size1":FieldTypeInfo("float",None, False), "size2":FieldTypeInfo("float",None, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return ATVLV0.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != ATVLV0:
            raise Exception("%s is not of type %s but %s" % (id, "ATVLV0", type(instance)))
        fieldId = id + ".bone0"

        if (type(instance.bone0) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".bone1"

        if (type(instance.bone1) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".type"

        if (type(instance.type) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".bone2"

        if (type(instance.bone2) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".matrix"

        Matrix44.validateInstance(instance.matrix, fieldId)
        fieldId = id + ".unknown0"

        if (type(instance.unknown0) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "VEC3V0", type(instance.unknown0)))
        for itemIndex, item in enumerate(instance.unknown0):
            VEC3V0.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".unknown1"
        if (type(instance.unknown1) != list):
            raise Exception("%s is not a list of integers" % (fieldId))
        for itemIndex, item in enumerate(instance.unknown1):
            itemId = "%s[%d]" % (fieldId, itemIndex)
            if type(item) != int: 
                raise Exception("%s is not an integer" % (itemId))
            if (item < 0) or (item > 131071):
                raise Exception("%s has value %d which is not in range [0, 131071]"  % (itemId, item))
        fieldId = id + ".size0"

        if (type(instance.size0) != float):
            raise Exception("%s is not a float" % (fieldId))
        fieldId = id + ".size1"

        if (type(instance.size1) != float):
            raise Exception("%s is not a float" % (fieldId))
        fieldId = id + ".size2"

        if (type(instance.size2) != float):
            raise Exception("%s is not a float" % (fieldId))


class BBSCV0:
    """
                Unknown
            """
    fullName = "BBSCV0"
    tagName = "BBSC"
    tagVersion = 0
    size = 48
    structFormat = struct.Struct("<48s")
    fields = ["unknown"]

    def __setattr__(self, name, value):
        if name in ["unknown"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["unknown"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        pass #nothing to do
    
    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        pass #nothing to do

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert BBSCV0.size == BBSCV0.structFormat.size
            rawBytes = readable.read(BBSCV0.size)
        if rawBytes != None:
            l = BBSCV0.structFormat.unpack(rawBytes)
            self.unknown = l[0]
        if (readable == None) and (rawBytes == None):
            self.unknown = bytes(48)
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + BBSCV0.size
        for i in range(count):
            list.append(BBSCV0(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += BBSCV0.size
        return list
    
    def toBytes(self):
        return BBSCV0.structFormat.pack(self.unknown)
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(BBSCV0.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = BBSCV0.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += BBSCV0.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return BBSCV0.countOneOrMore(object) * BBSCV0.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"unknown": {}}
    
    def getNamedBit(self, field, bitName):
        mask = BBSCV0.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = BBSCV0.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return BBSCV0.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"unknown":FieldTypeInfo(None,None, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return BBSCV0.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != BBSCV0:
            raise Exception("%s is not of type %s but %s" % (id, "BBSCV0", type(instance)))
        fieldId = id + ".unknown"

        if (type(instance.unknown) != bytes) or (len(instance.unknown) != 48):
            raise Exception("%s is not an bytes object of size %s" % (fieldId, "48"))


class SRIBV0:
    """
                Unknown
            """
    fullName = "SRIBV0"
    tagName = "SRIB"
    tagVersion = 0
    size = 272
    structFormat = struct.Struct("<272s")
    fields = ["unknown"]

    def __setattr__(self, name, value):
        if name in ["unknown"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["unknown"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        pass #nothing to do
    
    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        pass #nothing to do

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert SRIBV0.size == SRIBV0.structFormat.size
            rawBytes = readable.read(SRIBV0.size)
        if rawBytes != None:
            l = SRIBV0.structFormat.unpack(rawBytes)
            self.unknown = l[0]
        if (readable == None) and (rawBytes == None):
            self.unknown = bytes(272)
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + SRIBV0.size
        for i in range(count):
            list.append(SRIBV0(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += SRIBV0.size
        return list
    
    def toBytes(self):
        return SRIBV0.structFormat.pack(self.unknown)
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(SRIBV0.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = SRIBV0.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += SRIBV0.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return SRIBV0.countOneOrMore(object) * SRIBV0.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"unknown": {}}
    
    def getNamedBit(self, field, bitName):
        mask = SRIBV0.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = SRIBV0.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return SRIBV0.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"unknown":FieldTypeInfo(None,None, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return SRIBV0.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != SRIBV0:
            raise Exception("%s is not of type %s but %s" % (id, "SRIBV0", type(instance)))
        fieldId = id + ".unknown"

        if (type(instance.unknown) != bytes) or (len(instance.unknown) != 272):
            raise Exception("%s is not an bytes object of size %s" % (fieldId, "272"))


class RIB_V6:
    """
                Unknown
            """
    fullName = "RIB_V6"
    tagName = "RIB_"
    tagVersion = 6
    size = 748
    structFormat = struct.Struct("<436s12s300s")
    fields = ["unknown0", "sribData", "unknown1"]

    def __setattr__(self, name, value):
        if name in ["unknown0", "sribData", "unknown1"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["unknown0", "sribData", "unknown1"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    def resolveReferences(self, sections):
        self.sribData = resolveRef(self.sribData,sections,SRIBV0,"RIB_V6.sribData")


    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        if oneOrMore.__class__ == [].__class__:
            for object in oneOrMore:
                object.resolveReferences(sections) 
        else:
            oneOrMore.resolveReferences(sections)

    def introduceIndexReferences(self, indexMaker):
        indexReference = indexMaker.getIndexReferenceTo(self.sribData, Reference, SRIBV0)
        SRIBV0.introduceIndexReferencesForOneOrMore(self.sribData,  indexMaker)
        self.sribData = indexReference


    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        if object.__class__ == MD34IndexEntry:
            return # nothing to do (object was reachable trough 2 paths)
        if object.__class__ == [].__class__:
            for o in object:
                o.introduceIndexReferences(indexMaker) 
        else:
            object.introduceIndexReferences(indexMaker)

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert RIB_V6.size == RIB_V6.structFormat.size
            rawBytes = readable.read(RIB_V6.size)
        if rawBytes != None:
            l = RIB_V6.structFormat.unpack(rawBytes)
            self.unknown0 = l[0]
            self.sribData = Reference(rawBytes=l[1])
            self.unknown1 = l[2]
        if (readable == None) and (rawBytes == None):
            self.unknown0 = bytes(436)
            self.sribData = SRIBV0.createEmptyArray()
            self.unknown1 = bytes(300)
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + RIB_V6.size
        for i in range(count):
            list.append(RIB_V6(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += RIB_V6.size
        return list
    
    def toBytes(self):
        return RIB_V6.structFormat.pack(self.unknown0, self.sribData.toBytes(), self.unknown1)
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(RIB_V6.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = RIB_V6.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += RIB_V6.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return RIB_V6.countOneOrMore(object) * RIB_V6.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"unknown0": {}, "unknown1": {}, "sribData": {}}
    
    def getNamedBit(self, field, bitName):
        mask = RIB_V6.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = RIB_V6.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return RIB_V6.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"unknown0":FieldTypeInfo(None,None, False), "sribData":FieldTypeInfo("SRIBV0",SRIBV0, True), "unknown1":FieldTypeInfo(None,None, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return RIB_V6.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != RIB_V6:
            raise Exception("%s is not of type %s but %s" % (id, "RIB_V6", type(instance)))
        fieldId = id + ".unknown0"

        if (type(instance.unknown0) != bytes) or (len(instance.unknown0) != 436):
            raise Exception("%s is not an bytes object of size %s" % (fieldId, "436"))
        fieldId = id + ".sribData"

        if (type(instance.sribData) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "SRIBV0", type(instance.sribData)))
        for itemIndex, item in enumerate(instance.sribData):
            SRIBV0.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".unknown1"

        if (type(instance.unknown1) != bytes) or (len(instance.unknown1) != 300):
            raise Exception("%s is not an bytes object of size %s" % (fieldId, "300"))


class IKJTV0:
    """
                Unknown
            """
    fullName = "IKJTV0"
    tagName = "IKJT"
    tagVersion = 0
    size = 32
    structFormat = struct.Struct("<32s")
    fields = ["unknown"]

    def __setattr__(self, name, value):
        if name in ["unknown"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["unknown"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        pass #nothing to do
    
    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        pass #nothing to do

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert IKJTV0.size == IKJTV0.structFormat.size
            rawBytes = readable.read(IKJTV0.size)
        if rawBytes != None:
            l = IKJTV0.structFormat.unpack(rawBytes)
            self.unknown = l[0]
        if (readable == None) and (rawBytes == None):
            self.unknown = bytes(32)
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + IKJTV0.size
        for i in range(count):
            list.append(IKJTV0(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += IKJTV0.size
        return list
    
    def toBytes(self):
        return IKJTV0.structFormat.pack(self.unknown)
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(IKJTV0.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = IKJTV0.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += IKJTV0.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return IKJTV0.countOneOrMore(object) * IKJTV0.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"unknown": {}}
    
    def getNamedBit(self, field, bitName):
        mask = IKJTV0.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = IKJTV0.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return IKJTV0.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"unknown":FieldTypeInfo(None,None, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return IKJTV0.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != IKJTV0:
            raise Exception("%s is not of type %s but %s" % (id, "IKJTV0", type(instance)))
        fieldId = id + ".unknown"

        if (type(instance.unknown) != bytes) or (len(instance.unknown) != 32):
            raise Exception("%s is not an bytes object of size %s" % (fieldId, "32"))


class SHBXV0:
    """
                Unknown
            """
    fullName = "SHBXV0"
    tagName = "SHBX"
    tagVersion = 0
    size = 64
    structFormat = struct.Struct("<64s")
    fields = ["unknown"]

    def __setattr__(self, name, value):
        if name in ["unknown"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["unknown"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        pass #nothing to do
    
    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        pass #nothing to do

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert SHBXV0.size == SHBXV0.structFormat.size
            rawBytes = readable.read(SHBXV0.size)
        if rawBytes != None:
            l = SHBXV0.structFormat.unpack(rawBytes)
            self.unknown = l[0]
        if (readable == None) and (rawBytes == None):
            self.unknown = bytes(64)
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + SHBXV0.size
        for i in range(count):
            list.append(SHBXV0(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += SHBXV0.size
        return list
    
    def toBytes(self):
        return SHBXV0.structFormat.pack(self.unknown)
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(SHBXV0.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = SHBXV0.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += SHBXV0.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return SHBXV0.countOneOrMore(object) * SHBXV0.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"unknown": {}}
    
    def getNamedBit(self, field, bitName):
        mask = SHBXV0.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = SHBXV0.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return SHBXV0.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"unknown":FieldTypeInfo(None,None, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return SHBXV0.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != SHBXV0:
            raise Exception("%s is not of type %s but %s" % (id, "SHBXV0", type(instance)))
        fieldId = id + ".unknown"

        if (type(instance.unknown) != bytes) or (len(instance.unknown) != 64):
            raise Exception("%s is not an bytes object of size %s" % (fieldId, "64"))


class CAM_V3:
    """
                Camera
            """
    fullName = "CAM_V3"
    tagName = "CAM_"
    tagVersion = 3
    size = 180
    structFormat = struct.Struct("<4s12s20s4s20s20s20s20s20s20s20s")
    fields = ["unknown0", "name", "fovValue", "unknown1", "clipFar", "clipNear", "clip2", "focalDepth", "falloffStart", "falloffEnd", "dof"]

    def __setattr__(self, name, value):
        if name in ["unknown0", "name", "fovValue", "unknown1", "clipFar", "clipNear", "clip2", "focalDepth", "falloffStart", "falloffEnd", "dof"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["unknown0", "name", "fovValue", "unknown1", "clipFar", "clipNear", "clip2", "focalDepth", "falloffStart", "falloffEnd", "dof"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    def resolveReferences(self, sections):
        self.name = resolveRef(self.name,sections,CHARV0,"CAM_V3.name")


    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        if oneOrMore.__class__ == [].__class__:
            for object in oneOrMore:
                object.resolveReferences(sections) 
        else:
            oneOrMore.resolveReferences(sections)

    def introduceIndexReferences(self, indexMaker):
        indexReference = indexMaker.getIndexReferenceTo(self.name, Reference, CHARV0)
        CHARV0.introduceIndexReferencesForOneOrMore(self.name,  indexMaker)
        self.name = indexReference


    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        if object.__class__ == MD34IndexEntry:
            return # nothing to do (object was reachable trough 2 paths)
        if object.__class__ == [].__class__:
            for o in object:
                o.introduceIndexReferences(indexMaker) 
        else:
            object.introduceIndexReferences(indexMaker)

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert CAM_V3.size == CAM_V3.structFormat.size
            rawBytes = readable.read(CAM_V3.size)
        if rawBytes != None:
            l = CAM_V3.structFormat.unpack(rawBytes)
            self.unknown0 = l[0]
            self.name = Reference(rawBytes=l[1])
            self.fovValue = FloatAnimationReference(rawBytes=l[2])
            self.unknown1 = l[3]
            self.clipFar = FloatAnimationReference(rawBytes=l[4])
            self.clipNear = FloatAnimationReference(rawBytes=l[5])
            self.clip2 = FloatAnimationReference(rawBytes=l[6])
            self.focalDepth = FloatAnimationReference(rawBytes=l[7])
            self.falloffStart = FloatAnimationReference(rawBytes=l[8])
            self.falloffEnd = FloatAnimationReference(rawBytes=l[9])
            self.dof = FloatAnimationReference(rawBytes=l[10])
        if (readable == None) and (rawBytes == None):
            self.unknown0 = bytes(4)
            self.name = CHARV0.createEmptyArray()
            self.unknown1 = bytes(4)
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + CAM_V3.size
        for i in range(count):
            list.append(CAM_V3(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += CAM_V3.size
        return list
    
    def toBytes(self):
        return CAM_V3.structFormat.pack(self.unknown0, self.name.toBytes(), self.fovValue.toBytes(), self.unknown1, self.clipFar.toBytes(), self.clipNear.toBytes(), self.clip2.toBytes(), self.focalDepth.toBytes(), self.falloffStart.toBytes(), self.falloffEnd.toBytes(), self.dof.toBytes())
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(CAM_V3.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = CAM_V3.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += CAM_V3.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return CAM_V3.countOneOrMore(object) * CAM_V3.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"falloffStart": {}, "focalDepth": {}, "name": {}, "fovValue": {}, "dof": {}, "clip2": {}, "unknown0": {}, "unknown1": {}, "clipFar": {}, "clipNear": {}, "falloffEnd": {}}
    
    def getNamedBit(self, field, bitName):
        mask = CAM_V3.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = CAM_V3.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return CAM_V3.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"unknown0":FieldTypeInfo(None,None, False), "name":FieldTypeInfo("CHARV0",CHARV0, True), "fovValue":FieldTypeInfo("FloatAnimationReference",FloatAnimationReference, False), "unknown1":FieldTypeInfo(None,None, False), "clipFar":FieldTypeInfo("FloatAnimationReference",FloatAnimationReference, False), "clipNear":FieldTypeInfo("FloatAnimationReference",FloatAnimationReference, False), "clip2":FieldTypeInfo("FloatAnimationReference",FloatAnimationReference, False), "focalDepth":FieldTypeInfo("FloatAnimationReference",FloatAnimationReference, False), "falloffStart":FieldTypeInfo("FloatAnimationReference",FloatAnimationReference, False), "falloffEnd":FieldTypeInfo("FloatAnimationReference",FloatAnimationReference, False), "dof":FieldTypeInfo("FloatAnimationReference",FloatAnimationReference, False)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return CAM_V3.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != CAM_V3:
            raise Exception("%s is not of type %s but %s" % (id, "CAM_V3", type(instance)))
        fieldId = id + ".unknown0"

        if (type(instance.unknown0) != bytes) or (len(instance.unknown0) != 4):
            raise Exception("%s is not an bytes object of size %s" % (fieldId, "4"))
        fieldId = id + ".name"

        if (instance.name != None) and (type(instance.name) != str):
            raise Exception("%s is not a string but a %s" % (fieldId, type(instance.name) ))
        fieldId = id + ".fovValue"

        FloatAnimationReference.validateInstance(instance.fovValue, fieldId)
        fieldId = id + ".unknown1"

        if (type(instance.unknown1) != bytes) or (len(instance.unknown1) != 4):
            raise Exception("%s is not an bytes object of size %s" % (fieldId, "4"))
        fieldId = id + ".clipFar"

        FloatAnimationReference.validateInstance(instance.clipFar, fieldId)
        fieldId = id + ".clipNear"

        FloatAnimationReference.validateInstance(instance.clipNear, fieldId)
        fieldId = id + ".clip2"

        FloatAnimationReference.validateInstance(instance.clip2, fieldId)
        fieldId = id + ".focalDepth"

        FloatAnimationReference.validateInstance(instance.focalDepth, fieldId)
        fieldId = id + ".falloffStart"

        FloatAnimationReference.validateInstance(instance.falloffStart, fieldId)
        fieldId = id + ".falloffEnd"

        FloatAnimationReference.validateInstance(instance.falloffEnd, fieldId)
        fieldId = id + ".dof"

        FloatAnimationReference.validateInstance(instance.dof, fieldId)


class MODLV23:
    """
                Describes the content of the file.
                bone must have same size like IREF
            """
    fullName = "MODLV23"
    tagName = "MODL"
    tagVersion = 23
    size = 784
    structFormat = struct.Struct("<12sI12s12s12sffff12s12sII12s12s12s28sIIIIIIIIIIIIIIII12s12s12s12s12s12s12s12s12s12s12s12s12s12s12s12s12s12s12s12s12s12s12s12s12s12s12s12s12s12sII64sIIIIIIfff12s12s12s12s12s12sI12s")
    fields = ["modelName", "flags", "sequences", "sequenceTransformationCollections", "sequenceTransformationGroups", "unknown00", "unknown01", "unknown02", "unknown03", "sts", "bones", "numberOfBonesToCheckForSkin", "vFlags", "vertices", "divisions", "boneLookup", "boundings", "maybeBoundingsFlags", "unknown04", "unknown05", "unknown06", "unknown07", "unknown08", "unknown09", "unknown11", "unknown12", "unknown13", "unknown14", "unknown15", "unknown16", "unknown17", "unknown18", "unknown19", "attachmentPoints", "attachmentPointAddons", "lights", "shbxData", "cameras", "d", "materialReferences", "standardMaterials", "displacementMaterials", "compositeMaterials", "terrainMaterials", "volumeMaterials", "unknownMaybeRef0", "crepData", "particles", "particleCopies", "ribData", "projData", "forData", "wrpData", "unknownMaybeRef1", "phrbData", "unknownMaybeRef2", "unknownMaybeRef3", "unknownMaybeRef4", "ikjtData", "unknownMaybeRef5", "patuData", "trgdData", "absoluteInverseBoneRestPositions", "unknown32", "unknown34", "matrix", "unknown35", "unknown36", "unknown37", "unknown38", "unknown39", "unknown40", "unknown41", "unknown42", "unknown43", "SSGS", "attachmentVolumes", "attachmentVolumesAddon0", "attachmentVolumesAddon1", "bbscData", "tmdData", "uniqueUnknownNumber", "unknown45"]

    def __setattr__(self, name, value):
        if name in ["modelName", "flags", "sequences", "sequenceTransformationCollections", "sequenceTransformationGroups", "unknown00", "unknown01", "unknown02", "unknown03", "sts", "bones", "numberOfBonesToCheckForSkin", "vFlags", "vertices", "divisions", "boneLookup", "boundings", "maybeBoundingsFlags", "unknown04", "unknown05", "unknown06", "unknown07", "unknown08", "unknown09", "unknown11", "unknown12", "unknown13", "unknown14", "unknown15", "unknown16", "unknown17", "unknown18", "unknown19", "attachmentPoints", "attachmentPointAddons", "lights", "shbxData", "cameras", "d", "materialReferences", "standardMaterials", "displacementMaterials", "compositeMaterials", "terrainMaterials", "volumeMaterials", "unknownMaybeRef0", "crepData", "particles", "particleCopies", "ribData", "projData", "forData", "wrpData", "unknownMaybeRef1", "phrbData", "unknownMaybeRef2", "unknownMaybeRef3", "unknownMaybeRef4", "ikjtData", "unknownMaybeRef5", "patuData", "trgdData", "absoluteInverseBoneRestPositions", "unknown32", "unknown34", "matrix", "unknown35", "unknown36", "unknown37", "unknown38", "unknown39", "unknown40", "unknown41", "unknown42", "unknown43", "SSGS", "attachmentVolumes", "attachmentVolumesAddon0", "attachmentVolumesAddon1", "bbscData", "tmdData", "uniqueUnknownNumber", "unknown45"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["modelName", "flags", "sequences", "sequenceTransformationCollections", "sequenceTransformationGroups", "unknown00", "unknown01", "unknown02", "unknown03", "sts", "bones", "numberOfBonesToCheckForSkin", "vFlags", "vertices", "divisions", "boneLookup", "boundings", "maybeBoundingsFlags", "unknown04", "unknown05", "unknown06", "unknown07", "unknown08", "unknown09", "unknown11", "unknown12", "unknown13", "unknown14", "unknown15", "unknown16", "unknown17", "unknown18", "unknown19", "attachmentPoints", "attachmentPointAddons", "lights", "shbxData", "cameras", "d", "materialReferences", "standardMaterials", "displacementMaterials", "compositeMaterials", "terrainMaterials", "volumeMaterials", "unknownMaybeRef0", "crepData", "particles", "particleCopies", "ribData", "projData", "forData", "wrpData", "unknownMaybeRef1", "phrbData", "unknownMaybeRef2", "unknownMaybeRef3", "unknownMaybeRef4", "ikjtData", "unknownMaybeRef5", "patuData", "trgdData", "absoluteInverseBoneRestPositions", "unknown32", "unknown34", "matrix", "unknown35", "unknown36", "unknown37", "unknown38", "unknown39", "unknown40", "unknown41", "unknown42", "unknown43", "SSGS", "attachmentVolumes", "attachmentVolumesAddon0", "attachmentVolumesAddon1", "bbscData", "tmdData", "uniqueUnknownNumber", "unknown45"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    def resolveReferences(self, sections):
        self.modelName = resolveRef(self.modelName,sections,CHARV0,"MODLV23.modelName")
        self.sequences = resolveRef(self.sequences,sections,SEQSV1,"MODLV23.sequences")
        self.sequenceTransformationCollections = resolveRef(self.sequenceTransformationCollections,sections,STC_V4,"MODLV23.sequenceTransformationCollections")
        self.sequenceTransformationGroups = resolveRef(self.sequenceTransformationGroups,sections,STG_V0,"MODLV23.sequenceTransformationGroups")
        self.sts = resolveRef(self.sts,sections,STS_V0,"MODLV23.sts")
        self.bones = resolveRef(self.bones,sections,BONEV1,"MODLV23.bones")
        self.vertices = resolveRef(self.vertices,sections,U8__V0,"MODLV23.vertices")
        self.divisions = resolveRef(self.divisions,sections,DIV_V2,"MODLV23.divisions")
        self.boneLookup = resolveRef(self.boneLookup,sections,U16_V0,"MODLV23.boneLookup")
        self.attachmentPoints = resolveRef(self.attachmentPoints,sections,ATT_V1,"MODLV23.attachmentPoints")
        self.attachmentPointAddons = resolveRef(self.attachmentPointAddons,sections,U16_V0,"MODLV23.attachmentPointAddons")
        self.lights = resolveRef(self.lights,sections,LITEV7,"MODLV23.lights")
        self.shbxData = resolveRef(self.shbxData,sections,SHBXV0,"MODLV23.shbxData")
        self.cameras = resolveRef(self.cameras,sections,CAM_V3,"MODLV23.cameras")
        self.d = resolveRef(self.d,sections,U16_V0,"MODLV23.d")
        self.materialReferences = resolveRef(self.materialReferences,sections,MATMV0,"MODLV23.materialReferences")
        self.standardMaterials = resolveRef(self.standardMaterials,sections,MAT_V15,"MODLV23.standardMaterials")
        self.displacementMaterials = resolveRef(self.displacementMaterials,sections,DIS_V4,"MODLV23.displacementMaterials")
        self.compositeMaterials = resolveRef(self.compositeMaterials,sections,CMP_V2,"MODLV23.compositeMaterials")
        self.terrainMaterials = resolveRef(self.terrainMaterials,sections,TER_V0,"MODLV23.terrainMaterials")
        self.volumeMaterials = resolveRef(self.volumeMaterials,sections,VOL_V0,"MODLV23.volumeMaterials")
        self.unknownMaybeRef0 = resolveRef(self.unknownMaybeRef0,sections,None,"MODLV23.unknownMaybeRef0")
        self.crepData = resolveRef(self.crepData,sections,None,"MODLV23.crepData")
        self.particles = resolveRef(self.particles,sections,PAR_V12,"MODLV23.particles")
        self.particleCopies = resolveRef(self.particleCopies,sections,PARCV0,"MODLV23.particleCopies")
        self.ribData = resolveRef(self.ribData,sections,RIB_V6,"MODLV23.ribData")
        self.projData = resolveRef(self.projData,sections,PROJV4,"MODLV23.projData")
        self.forData = resolveRef(self.forData,sections,FOR_V1,"MODLV23.forData")
        self.wrpData = resolveRef(self.wrpData,sections,None,"MODLV23.wrpData")
        self.unknownMaybeRef1 = resolveRef(self.unknownMaybeRef1,sections,None,"MODLV23.unknownMaybeRef1")
        self.phrbData = resolveRef(self.phrbData,sections,PHRBV2,"MODLV23.phrbData")
        self.unknownMaybeRef2 = resolveRef(self.unknownMaybeRef2,sections,None,"MODLV23.unknownMaybeRef2")
        self.unknownMaybeRef3 = resolveRef(self.unknownMaybeRef3,sections,None,"MODLV23.unknownMaybeRef3")
        self.unknownMaybeRef4 = resolveRef(self.unknownMaybeRef4,sections,None,"MODLV23.unknownMaybeRef4")
        self.ikjtData = resolveRef(self.ikjtData,sections,IKJTV0,"MODLV23.ikjtData")
        self.unknownMaybeRef5 = resolveRef(self.unknownMaybeRef5,sections,None,"MODLV23.unknownMaybeRef5")
        self.patuData = resolveRef(self.patuData,sections,PATUV4,"MODLV23.patuData")
        self.trgdData = resolveRef(self.trgdData,sections,TRGDV0,"MODLV23.trgdData")
        self.absoluteInverseBoneRestPositions = resolveRef(self.absoluteInverseBoneRestPositions,sections,IREFV0,"MODLV23.absoluteInverseBoneRestPositions")
        self.SSGS = resolveRef(self.SSGS,sections,SSGSV1,"MODLV23.SSGS")
        self.attachmentVolumes = resolveRef(self.attachmentVolumes,sections,ATVLV0,"MODLV23.attachmentVolumes")
        self.attachmentVolumesAddon0 = resolveRef(self.attachmentVolumesAddon0,sections,U16_V0,"MODLV23.attachmentVolumesAddon0")
        self.attachmentVolumesAddon1 = resolveRef(self.attachmentVolumesAddon1,sections,U16_V0,"MODLV23.attachmentVolumesAddon1")
        self.bbscData = resolveRef(self.bbscData,sections,BBSCV0,"MODLV23.bbscData")
        self.tmdData = resolveRef(self.tmdData,sections,None,"MODLV23.tmdData")
        self.unknown45 = resolveRef(self.unknown45,sections,U32_V0,"MODLV23.unknown45")


    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        if oneOrMore.__class__ == [].__class__:
            for object in oneOrMore:
                object.resolveReferences(sections) 
        else:
            oneOrMore.resolveReferences(sections)

    def introduceIndexReferences(self, indexMaker):
        indexReference = indexMaker.getIndexReferenceTo(self.modelName, Reference, CHARV0)
        CHARV0.introduceIndexReferencesForOneOrMore(self.modelName,  indexMaker)
        self.modelName = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.sequences, Reference, SEQSV1)
        SEQSV1.introduceIndexReferencesForOneOrMore(self.sequences,  indexMaker)
        self.sequences = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.sequenceTransformationCollections, Reference, STC_V4)
        STC_V4.introduceIndexReferencesForOneOrMore(self.sequenceTransformationCollections,  indexMaker)
        self.sequenceTransformationCollections = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.sequenceTransformationGroups, Reference, STG_V0)
        STG_V0.introduceIndexReferencesForOneOrMore(self.sequenceTransformationGroups,  indexMaker)
        self.sequenceTransformationGroups = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.sts, Reference, STS_V0)
        STS_V0.introduceIndexReferencesForOneOrMore(self.sts,  indexMaker)
        self.sts = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.bones, Reference, BONEV1)
        BONEV1.introduceIndexReferencesForOneOrMore(self.bones,  indexMaker)
        self.bones = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.vertices, Reference, U8__V0)
        U8__V0.introduceIndexReferencesForOneOrMore(self.vertices,  indexMaker)
        self.vertices = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.divisions, Reference, DIV_V2)
        DIV_V2.introduceIndexReferencesForOneOrMore(self.divisions,  indexMaker)
        self.divisions = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.boneLookup, Reference, U16_V0)
        U16_V0.introduceIndexReferencesForOneOrMore(self.boneLookup,  indexMaker)
        self.boneLookup = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.attachmentPoints, Reference, ATT_V1)
        ATT_V1.introduceIndexReferencesForOneOrMore(self.attachmentPoints,  indexMaker)
        self.attachmentPoints = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.attachmentPointAddons, Reference, U16_V0)
        U16_V0.introduceIndexReferencesForOneOrMore(self.attachmentPointAddons,  indexMaker)
        self.attachmentPointAddons = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.lights, Reference, LITEV7)
        LITEV7.introduceIndexReferencesForOneOrMore(self.lights,  indexMaker)
        self.lights = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.shbxData, Reference, SHBXV0)
        SHBXV0.introduceIndexReferencesForOneOrMore(self.shbxData,  indexMaker)
        self.shbxData = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.cameras, Reference, CAM_V3)
        CAM_V3.introduceIndexReferencesForOneOrMore(self.cameras,  indexMaker)
        self.cameras = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.d, Reference, U16_V0)
        U16_V0.introduceIndexReferencesForOneOrMore(self.d,  indexMaker)
        self.d = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.materialReferences, Reference, MATMV0)
        MATMV0.introduceIndexReferencesForOneOrMore(self.materialReferences,  indexMaker)
        self.materialReferences = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.standardMaterials, Reference, MAT_V15)
        MAT_V15.introduceIndexReferencesForOneOrMore(self.standardMaterials,  indexMaker)
        self.standardMaterials = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.displacementMaterials, Reference, DIS_V4)
        DIS_V4.introduceIndexReferencesForOneOrMore(self.displacementMaterials,  indexMaker)
        self.displacementMaterials = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.compositeMaterials, Reference, CMP_V2)
        CMP_V2.introduceIndexReferencesForOneOrMore(self.compositeMaterials,  indexMaker)
        self.compositeMaterials = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.terrainMaterials, Reference, TER_V0)
        TER_V0.introduceIndexReferencesForOneOrMore(self.terrainMaterials,  indexMaker)
        self.terrainMaterials = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.volumeMaterials, Reference, VOL_V0)
        VOL_V0.introduceIndexReferencesForOneOrMore(self.volumeMaterials,  indexMaker)
        self.volumeMaterials = indexReference
        self.unknownMaybeRef0 = indexMaker.getIndexReferenceTo(self.unknownMaybeRef0, Reference, None)
        self.crepData = indexMaker.getIndexReferenceTo(self.crepData, Reference, None)
        indexReference = indexMaker.getIndexReferenceTo(self.particles, Reference, PAR_V12)
        PAR_V12.introduceIndexReferencesForOneOrMore(self.particles,  indexMaker)
        self.particles = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.particleCopies, Reference, PARCV0)
        PARCV0.introduceIndexReferencesForOneOrMore(self.particleCopies,  indexMaker)
        self.particleCopies = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.ribData, Reference, RIB_V6)
        RIB_V6.introduceIndexReferencesForOneOrMore(self.ribData,  indexMaker)
        self.ribData = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.projData, Reference, PROJV4)
        PROJV4.introduceIndexReferencesForOneOrMore(self.projData,  indexMaker)
        self.projData = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.forData, Reference, FOR_V1)
        FOR_V1.introduceIndexReferencesForOneOrMore(self.forData,  indexMaker)
        self.forData = indexReference
        self.wrpData = indexMaker.getIndexReferenceTo(self.wrpData, Reference, None)
        self.unknownMaybeRef1 = indexMaker.getIndexReferenceTo(self.unknownMaybeRef1, Reference, None)
        indexReference = indexMaker.getIndexReferenceTo(self.phrbData, Reference, PHRBV2)
        PHRBV2.introduceIndexReferencesForOneOrMore(self.phrbData,  indexMaker)
        self.phrbData = indexReference
        self.unknownMaybeRef2 = indexMaker.getIndexReferenceTo(self.unknownMaybeRef2, Reference, None)
        self.unknownMaybeRef3 = indexMaker.getIndexReferenceTo(self.unknownMaybeRef3, Reference, None)
        self.unknownMaybeRef4 = indexMaker.getIndexReferenceTo(self.unknownMaybeRef4, Reference, None)
        indexReference = indexMaker.getIndexReferenceTo(self.ikjtData, Reference, IKJTV0)
        IKJTV0.introduceIndexReferencesForOneOrMore(self.ikjtData,  indexMaker)
        self.ikjtData = indexReference
        self.unknownMaybeRef5 = indexMaker.getIndexReferenceTo(self.unknownMaybeRef5, Reference, None)
        indexReference = indexMaker.getIndexReferenceTo(self.patuData, Reference, PATUV4)
        PATUV4.introduceIndexReferencesForOneOrMore(self.patuData,  indexMaker)
        self.patuData = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.trgdData, Reference, TRGDV0)
        TRGDV0.introduceIndexReferencesForOneOrMore(self.trgdData,  indexMaker)
        self.trgdData = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.absoluteInverseBoneRestPositions, Reference, IREFV0)
        IREFV0.introduceIndexReferencesForOneOrMore(self.absoluteInverseBoneRestPositions,  indexMaker)
        self.absoluteInverseBoneRestPositions = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.SSGS, Reference, SSGSV1)
        SSGSV1.introduceIndexReferencesForOneOrMore(self.SSGS,  indexMaker)
        self.SSGS = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.attachmentVolumes, Reference, ATVLV0)
        ATVLV0.introduceIndexReferencesForOneOrMore(self.attachmentVolumes,  indexMaker)
        self.attachmentVolumes = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.attachmentVolumesAddon0, Reference, U16_V0)
        U16_V0.introduceIndexReferencesForOneOrMore(self.attachmentVolumesAddon0,  indexMaker)
        self.attachmentVolumesAddon0 = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.attachmentVolumesAddon1, Reference, U16_V0)
        U16_V0.introduceIndexReferencesForOneOrMore(self.attachmentVolumesAddon1,  indexMaker)
        self.attachmentVolumesAddon1 = indexReference
        indexReference = indexMaker.getIndexReferenceTo(self.bbscData, Reference, BBSCV0)
        BBSCV0.introduceIndexReferencesForOneOrMore(self.bbscData,  indexMaker)
        self.bbscData = indexReference
        self.tmdData = indexMaker.getIndexReferenceTo(self.tmdData, Reference, None)
        indexReference = indexMaker.getIndexReferenceTo(self.unknown45, Reference, U32_V0)
        U32_V0.introduceIndexReferencesForOneOrMore(self.unknown45,  indexMaker)
        self.unknown45 = indexReference


    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        if object.__class__ == MD34IndexEntry:
            return # nothing to do (object was reachable trough 2 paths)
        if object.__class__ == [].__class__:
            for o in object:
                o.introduceIndexReferences(indexMaker) 
        else:
            object.introduceIndexReferences(indexMaker)

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert MODLV23.size == MODLV23.structFormat.size
            rawBytes = readable.read(MODLV23.size)
        if rawBytes != None:
            l = MODLV23.structFormat.unpack(rawBytes)
            self.modelName = Reference(rawBytes=l[0])
            self.flags = l[1]
            self.sequences = Reference(rawBytes=l[2])
            self.sequenceTransformationCollections = Reference(rawBytes=l[3])
            self.sequenceTransformationGroups = Reference(rawBytes=l[4])
            self.unknown00 = l[5]
            if self.unknown00 != 0.0:
             raise Exception("MODLV23.unknown00 has value %s instead of the expected value 0.0" % self.unknown00)
            self.unknown01 = l[6]
            if self.unknown01 != 0.0:
             raise Exception("MODLV23.unknown01 has value %s instead of the expected value 0.0" % self.unknown01)
            self.unknown02 = l[7]
            if self.unknown02 != 0.0:
             raise Exception("MODLV23.unknown02 has value %s instead of the expected value 0.0" % self.unknown02)
            self.unknown03 = l[8]
            if self.unknown03 != 0.0:
             raise Exception("MODLV23.unknown03 has value %s instead of the expected value 0.0" % self.unknown03)
            self.sts = Reference(rawBytes=l[9])
            self.bones = Reference(rawBytes=l[10])
            self.numberOfBonesToCheckForSkin = l[11]
            self.vFlags = l[12]
            self.vertices = Reference(rawBytes=l[13])
            self.divisions = Reference(rawBytes=l[14])
            self.boneLookup = Reference(rawBytes=l[15])
            self.boundings = BNDSV0(rawBytes=l[16])
            self.maybeBoundingsFlags = l[17]
            if self.maybeBoundingsFlags != int(0):
             raise Exception("MODLV23.maybeBoundingsFlags has value %s instead of the expected value int(0)" % self.maybeBoundingsFlags)
            self.unknown04 = l[18]
            if self.unknown04 != int(0):
             raise Exception("MODLV23.unknown04 has value %s instead of the expected value int(0)" % self.unknown04)
            self.unknown05 = l[19]
            if self.unknown05 != int(0):
             raise Exception("MODLV23.unknown05 has value %s instead of the expected value int(0)" % self.unknown05)
            self.unknown06 = l[20]
            if self.unknown06 != int(0):
             raise Exception("MODLV23.unknown06 has value %s instead of the expected value int(0)" % self.unknown06)
            self.unknown07 = l[21]
            if self.unknown07 != int(0):
             raise Exception("MODLV23.unknown07 has value %s instead of the expected value int(0)" % self.unknown07)
            self.unknown08 = l[22]
            if self.unknown08 != int(0):
             raise Exception("MODLV23.unknown08 has value %s instead of the expected value int(0)" % self.unknown08)
            self.unknown09 = l[23]
            if self.unknown09 != int(0):
             raise Exception("MODLV23.unknown09 has value %s instead of the expected value int(0)" % self.unknown09)
            self.unknown11 = l[24]
            if self.unknown11 != int(0):
             raise Exception("MODLV23.unknown11 has value %s instead of the expected value int(0)" % self.unknown11)
            self.unknown12 = l[25]
            if self.unknown12 != int(0):
             raise Exception("MODLV23.unknown12 has value %s instead of the expected value int(0)" % self.unknown12)
            self.unknown13 = l[26]
            if self.unknown13 != int(0):
             raise Exception("MODLV23.unknown13 has value %s instead of the expected value int(0)" % self.unknown13)
            self.unknown14 = l[27]
            if self.unknown14 != int(0):
             raise Exception("MODLV23.unknown14 has value %s instead of the expected value int(0)" % self.unknown14)
            self.unknown15 = l[28]
            if self.unknown15 != int(0):
             raise Exception("MODLV23.unknown15 has value %s instead of the expected value int(0)" % self.unknown15)
            self.unknown16 = l[29]
            if self.unknown16 != int(0):
             raise Exception("MODLV23.unknown16 has value %s instead of the expected value int(0)" % self.unknown16)
            self.unknown17 = l[30]
            if self.unknown17 != int(0):
             raise Exception("MODLV23.unknown17 has value %s instead of the expected value int(0)" % self.unknown17)
            self.unknown18 = l[31]
            if self.unknown18 != int(0):
             raise Exception("MODLV23.unknown18 has value %s instead of the expected value int(0)" % self.unknown18)
            self.unknown19 = l[32]
            if self.unknown19 != int(0):
             raise Exception("MODLV23.unknown19 has value %s instead of the expected value int(0)" % self.unknown19)
            self.attachmentPoints = Reference(rawBytes=l[33])
            self.attachmentPointAddons = Reference(rawBytes=l[34])
            self.lights = Reference(rawBytes=l[35])
            self.shbxData = Reference(rawBytes=l[36])
            self.cameras = Reference(rawBytes=l[37])
            self.d = Reference(rawBytes=l[38])
            self.materialReferences = Reference(rawBytes=l[39])
            self.standardMaterials = Reference(rawBytes=l[40])
            self.displacementMaterials = Reference(rawBytes=l[41])
            self.compositeMaterials = Reference(rawBytes=l[42])
            self.terrainMaterials = Reference(rawBytes=l[43])
            self.volumeMaterials = Reference(rawBytes=l[44])
            self.unknownMaybeRef0 = Reference(rawBytes=l[45])
            self.crepData = Reference(rawBytes=l[46])
            self.particles = Reference(rawBytes=l[47])
            self.particleCopies = Reference(rawBytes=l[48])
            self.ribData = Reference(rawBytes=l[49])
            self.projData = Reference(rawBytes=l[50])
            self.forData = Reference(rawBytes=l[51])
            self.wrpData = Reference(rawBytes=l[52])
            self.unknownMaybeRef1 = Reference(rawBytes=l[53])
            self.phrbData = Reference(rawBytes=l[54])
            self.unknownMaybeRef2 = Reference(rawBytes=l[55])
            self.unknownMaybeRef3 = Reference(rawBytes=l[56])
            self.unknownMaybeRef4 = Reference(rawBytes=l[57])
            self.ikjtData = Reference(rawBytes=l[58])
            self.unknownMaybeRef5 = Reference(rawBytes=l[59])
            self.patuData = Reference(rawBytes=l[60])
            self.trgdData = Reference(rawBytes=l[61])
            self.absoluteInverseBoneRestPositions = Reference(rawBytes=l[62])
            self.unknown32 = l[63]
            self.unknown34 = l[64]
            self.matrix = Matrix44(rawBytes=l[65])
            self.unknown35 = l[66]
            if self.unknown35 != int(0):
             raise Exception("MODLV23.unknown35 has value %s instead of the expected value int(0)" % self.unknown35)
            self.unknown36 = l[67]
            if self.unknown36 != int(0):
             raise Exception("MODLV23.unknown36 has value %s instead of the expected value int(0)" % self.unknown36)
            self.unknown37 = l[68]
            if self.unknown37 != int(0):
             raise Exception("MODLV23.unknown37 has value %s instead of the expected value int(0)" % self.unknown37)
            self.unknown38 = l[69]
            if self.unknown38 != int(0):
             raise Exception("MODLV23.unknown38 has value %s instead of the expected value int(0)" % self.unknown38)
            self.unknown39 = l[70]
            if self.unknown39 != int(0):
             raise Exception("MODLV23.unknown39 has value %s instead of the expected value int(0)" % self.unknown39)
            self.unknown40 = l[71]
            if self.unknown40 != int(0):
             raise Exception("MODLV23.unknown40 has value %s instead of the expected value int(0)" % self.unknown40)
            self.unknown41 = l[72]
            self.unknown42 = l[73]
            self.unknown43 = l[74]
            self.SSGS = Reference(rawBytes=l[75])
            self.attachmentVolumes = Reference(rawBytes=l[76])
            self.attachmentVolumesAddon0 = Reference(rawBytes=l[77])
            self.attachmentVolumesAddon1 = Reference(rawBytes=l[78])
            self.bbscData = Reference(rawBytes=l[79])
            self.tmdData = Reference(rawBytes=l[80])
            self.uniqueUnknownNumber = l[81]
            self.unknown45 = Reference(rawBytes=l[82])
        if (readable == None) and (rawBytes == None):
            self.modelName = CHARV0.createEmptyArray()
            self.flags = 0x80d53
            self.sequences = SEQSV1.createEmptyArray()
            self.sequenceTransformationCollections = STC_V4.createEmptyArray()
            self.sequenceTransformationGroups = STG_V0.createEmptyArray()
            self.unknown00 = 0.0
            self.unknown01 = 0.0
            self.unknown02 = 0.0
            self.unknown03 = 0.0
            self.sts = STS_V0.createEmptyArray()
            self.bones = BONEV1.createEmptyArray()
            self.vFlags = 0x180007d
            self.vertices = U8__V0.createEmptyArray()
            self.divisions = DIV_V2.createEmptyArray()
            self.boneLookup = U16_V0.createEmptyArray()
            self.maybeBoundingsFlags = int(0)
            self.unknown04 = int(0)
            self.unknown05 = int(0)
            self.unknown06 = int(0)
            self.unknown07 = int(0)
            self.unknown08 = int(0)
            self.unknown09 = int(0)
            self.unknown11 = int(0)
            self.unknown12 = int(0)
            self.unknown13 = int(0)
            self.unknown14 = int(0)
            self.unknown15 = int(0)
            self.unknown16 = int(0)
            self.unknown17 = int(0)
            self.unknown18 = int(0)
            self.unknown19 = int(0)
            self.attachmentPoints = ATT_V1.createEmptyArray()
            self.attachmentPointAddons = U16_V0.createEmptyArray()
            self.lights = LITEV7.createEmptyArray()
            self.shbxData = SHBXV0.createEmptyArray()
            self.cameras = CAM_V3.createEmptyArray()
            self.d = U16_V0.createEmptyArray()
            self.materialReferences = MATMV0.createEmptyArray()
            self.standardMaterials = MAT_V15.createEmptyArray()
            self.displacementMaterials = DIS_V4.createEmptyArray()
            self.compositeMaterials = CMP_V2.createEmptyArray()
            self.terrainMaterials = TER_V0.createEmptyArray()
            self.volumeMaterials = VOL_V0.createEmptyArray()
            self.unknownMaybeRef0 = []
            self.crepData = []
            self.particles = PAR_V12.createEmptyArray()
            self.particleCopies = PARCV0.createEmptyArray()
            self.ribData = RIB_V6.createEmptyArray()
            self.projData = PROJV4.createEmptyArray()
            self.forData = FOR_V1.createEmptyArray()
            self.wrpData = []
            self.unknownMaybeRef1 = []
            self.phrbData = PHRBV2.createEmptyArray()
            self.unknownMaybeRef2 = []
            self.unknownMaybeRef3 = []
            self.unknownMaybeRef4 = []
            self.ikjtData = IKJTV0.createEmptyArray()
            self.unknownMaybeRef5 = []
            self.patuData = PATUV4.createEmptyArray()
            self.trgdData = TRGDV0.createEmptyArray()
            self.absoluteInverseBoneRestPositions = IREFV0.createEmptyArray()
            self.unknown32 = 1
            self.unknown34 = 0xffff
            self.unknown35 = int(0)
            self.unknown36 = int(0)
            self.unknown37 = int(0)
            self.unknown38 = int(0)
            self.unknown39 = int(0)
            self.unknown40 = int(0)
            self.unknown41 = 0.0
            self.unknown42 = 0.0
            self.unknown43 = 0.0
            self.SSGS = SSGSV1.createEmptyArray()
            self.attachmentVolumes = ATVLV0.createEmptyArray()
            self.attachmentVolumesAddon0 = U16_V0.createEmptyArray()
            self.attachmentVolumesAddon1 = U16_V0.createEmptyArray()
            self.bbscData = BBSCV0.createEmptyArray()
            self.tmdData = []
            self.unknown45 = U32_V0.createEmptyArray()
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + MODLV23.size
        for i in range(count):
            list.append(MODLV23(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += MODLV23.size
        return list
    
    def toBytes(self):
        return MODLV23.structFormat.pack(self.modelName.toBytes(), self.flags, self.sequences.toBytes(), self.sequenceTransformationCollections.toBytes(), self.sequenceTransformationGroups.toBytes(), self.unknown00, self.unknown01, self.unknown02, self.unknown03, self.sts.toBytes(), self.bones.toBytes(), self.numberOfBonesToCheckForSkin, self.vFlags, self.vertices.toBytes(), self.divisions.toBytes(), self.boneLookup.toBytes(), self.boundings.toBytes(), self.maybeBoundingsFlags, self.unknown04, self.unknown05, self.unknown06, self.unknown07, self.unknown08, self.unknown09, self.unknown11, self.unknown12, self.unknown13, self.unknown14, self.unknown15, self.unknown16, self.unknown17, self.unknown18, self.unknown19, self.attachmentPoints.toBytes(), self.attachmentPointAddons.toBytes(), self.lights.toBytes(), self.shbxData.toBytes(), self.cameras.toBytes(), self.d.toBytes(), self.materialReferences.toBytes(), self.standardMaterials.toBytes(), self.displacementMaterials.toBytes(), self.compositeMaterials.toBytes(), self.terrainMaterials.toBytes(), self.volumeMaterials.toBytes(), self.unknownMaybeRef0.toBytes(), self.crepData.toBytes(), self.particles.toBytes(), self.particleCopies.toBytes(), self.ribData.toBytes(), self.projData.toBytes(), self.forData.toBytes(), self.wrpData.toBytes(), self.unknownMaybeRef1.toBytes(), self.phrbData.toBytes(), self.unknownMaybeRef2.toBytes(), self.unknownMaybeRef3.toBytes(), self.unknownMaybeRef4.toBytes(), self.ikjtData.toBytes(), self.unknownMaybeRef5.toBytes(), self.patuData.toBytes(), self.trgdData.toBytes(), self.absoluteInverseBoneRestPositions.toBytes(), self.unknown32, self.unknown34, self.matrix.toBytes(), self.unknown35, self.unknown36, self.unknown37, self.unknown38, self.unknown39, self.unknown40, self.unknown41, self.unknown42, self.unknown43, self.SSGS.toBytes(), self.attachmentVolumes.toBytes(), self.attachmentVolumesAddon0.toBytes(), self.attachmentVolumesAddon1.toBytes(), self.bbscData.toBytes(), self.tmdData.toBytes(), self.uniqueUnknownNumber, self.unknown45.toBytes())
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(MODLV23.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = MODLV23.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += MODLV23.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return MODLV23.countOneOrMore(object) * MODLV23.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"unknown43": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "unknown42": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "unknown41": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "unknown40": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "sequenceTransformationCollections": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "unknown45": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "boneLookup": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "unknown00": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "unknownMaybeRef2": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "unknown07": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "unknown06": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "unknown05": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "unknown04": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "unknown03": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "unknown02": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "unknown01": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "sequences": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "bones": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "attachmentVolumesAddon1": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "attachmentPoints": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "volumeMaterials": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "forData": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "unknown09": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "unknown08": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "tmdData": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "modelName": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "matrix": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "bbscData": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "maybeBoundingsFlags": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "cameras": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "crepData": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "unknownMaybeRef5": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "particles": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "lights": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "attachmentVolumes": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "uniqueUnknownNumber": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "flags": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "displacementMaterials": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "boundings": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "terrainMaterials": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "unknown18": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "unknown19": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "compositeMaterials": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "projData": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "unknown11": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "unknown12": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "unknown13": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "unknown14": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "unknown15": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "unknown16": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "unknown17": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "unknown32": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "ribData": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "shbxData": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "unknown36": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "unknown37": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "unknown34": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "unknown35": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "unknown38": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "unknown39": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "materialReferences": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "attachmentPointAddons": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "divisions": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "standardMaterials": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "unknownMaybeRef4": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "unknownMaybeRef3": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "d": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "unknownMaybeRef1": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "unknownMaybeRef0": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "ikjtData": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "numberOfBonesToCheckForSkin": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "phrbData": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "vertices": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "patuData": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "absoluteInverseBoneRestPositions": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "sequenceTransformationGroups": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "attachmentVolumesAddon0": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "sts": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "particleCopies": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "vFlags": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "trgdData": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "SSGS": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}, "wrpData": {"hasMesh":0x100000, "useUVChannel2":0x80000, "useUVChannel1":0x40000, "hasVertices":0x20000, "useUVChannel3":0x100000}}
    
    def getNamedBit(self, field, bitName):
        mask = MODLV23.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = MODLV23.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return MODLV23.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"modelName":FieldTypeInfo("CHARV0",CHARV0, True), "flags":FieldTypeInfo("uint32",None, False), "sequences":FieldTypeInfo("SEQSV1",SEQSV1, True), "sequenceTransformationCollections":FieldTypeInfo("STC_V4",STC_V4, True), "sequenceTransformationGroups":FieldTypeInfo("STG_V0",STG_V0, True), "unknown00":FieldTypeInfo("float",None, False), "unknown01":FieldTypeInfo("float",None, False), "unknown02":FieldTypeInfo("float",None, False), "unknown03":FieldTypeInfo("float",None, False), "sts":FieldTypeInfo("STS_V0",STS_V0, True), "bones":FieldTypeInfo("BONEV1",BONEV1, True), "numberOfBonesToCheckForSkin":FieldTypeInfo("uint32",None, False), "vFlags":FieldTypeInfo("uint32",None, False), "vertices":FieldTypeInfo("U8__V0",U8__V0, True), "divisions":FieldTypeInfo("DIV_V2",DIV_V2, True), "boneLookup":FieldTypeInfo("U16_V0",U16_V0, True), "boundings":FieldTypeInfo("BNDSV0",BNDSV0, False), "maybeBoundingsFlags":FieldTypeInfo("uint32",None, False), "unknown04":FieldTypeInfo("uint32",None, False), "unknown05":FieldTypeInfo("uint32",None, False), "unknown06":FieldTypeInfo("uint32",None, False), "unknown07":FieldTypeInfo("uint32",None, False), "unknown08":FieldTypeInfo("uint32",None, False), "unknown09":FieldTypeInfo("uint32",None, False), "unknown11":FieldTypeInfo("uint32",None, False), "unknown12":FieldTypeInfo("uint32",None, False), "unknown13":FieldTypeInfo("uint32",None, False), "unknown14":FieldTypeInfo("uint32",None, False), "unknown15":FieldTypeInfo("uint32",None, False), "unknown16":FieldTypeInfo("uint32",None, False), "unknown17":FieldTypeInfo("uint32",None, False), "unknown18":FieldTypeInfo("uint32",None, False), "unknown19":FieldTypeInfo("uint32",None, False), "attachmentPoints":FieldTypeInfo("ATT_V1",ATT_V1, True), "attachmentPointAddons":FieldTypeInfo("U16_V0",U16_V0, True), "lights":FieldTypeInfo("LITEV7",LITEV7, True), "shbxData":FieldTypeInfo("SHBXV0",SHBXV0, True), "cameras":FieldTypeInfo("CAM_V3",CAM_V3, True), "d":FieldTypeInfo("U16_V0",U16_V0, True), "materialReferences":FieldTypeInfo("MATMV0",MATMV0, True), "standardMaterials":FieldTypeInfo("MAT_V15",MAT_V15, True), "displacementMaterials":FieldTypeInfo("DIS_V4",DIS_V4, True), "compositeMaterials":FieldTypeInfo("CMP_V2",CMP_V2, True), "terrainMaterials":FieldTypeInfo("TER_V0",TER_V0, True), "volumeMaterials":FieldTypeInfo("VOL_V0",VOL_V0, True), "unknownMaybeRef0":FieldTypeInfo(None,None, True), "crepData":FieldTypeInfo(None,None, True), "particles":FieldTypeInfo("PAR_V12",PAR_V12, True), "particleCopies":FieldTypeInfo("PARCV0",PARCV0, True), "ribData":FieldTypeInfo("RIB_V6",RIB_V6, True), "projData":FieldTypeInfo("PROJV4",PROJV4, True), "forData":FieldTypeInfo("FOR_V1",FOR_V1, True), "wrpData":FieldTypeInfo(None,None, True), "unknownMaybeRef1":FieldTypeInfo(None,None, True), "phrbData":FieldTypeInfo("PHRBV2",PHRBV2, True), "unknownMaybeRef2":FieldTypeInfo(None,None, True), "unknownMaybeRef3":FieldTypeInfo(None,None, True), "unknownMaybeRef4":FieldTypeInfo(None,None, True), "ikjtData":FieldTypeInfo("IKJTV0",IKJTV0, True), "unknownMaybeRef5":FieldTypeInfo(None,None, True), "patuData":FieldTypeInfo("PATUV4",PATUV4, True), "trgdData":FieldTypeInfo("TRGDV0",TRGDV0, True), "absoluteInverseBoneRestPositions":FieldTypeInfo("IREFV0",IREFV0, True), "unknown32":FieldTypeInfo("uint32",None, False), "unknown34":FieldTypeInfo("uint32",None, False), "matrix":FieldTypeInfo("Matrix44",Matrix44, False), "unknown35":FieldTypeInfo("uint32",None, False), "unknown36":FieldTypeInfo("uint32",None, False), "unknown37":FieldTypeInfo("uint32",None, False), "unknown38":FieldTypeInfo("uint32",None, False), "unknown39":FieldTypeInfo("uint32",None, False), "unknown40":FieldTypeInfo("uint32",None, False), "unknown41":FieldTypeInfo("float",None, False), "unknown42":FieldTypeInfo("float",None, False), "unknown43":FieldTypeInfo("float",None, False), "SSGS":FieldTypeInfo("SSGSV1",SSGSV1, True), "attachmentVolumes":FieldTypeInfo("ATVLV0",ATVLV0, True), "attachmentVolumesAddon0":FieldTypeInfo("U16_V0",U16_V0, True), "attachmentVolumesAddon1":FieldTypeInfo("U16_V0",U16_V0, True), "bbscData":FieldTypeInfo("BBSCV0",BBSCV0, True), "tmdData":FieldTypeInfo(None,None, True), "uniqueUnknownNumber":FieldTypeInfo("uint32",None, False), "unknown45":FieldTypeInfo("U32_V0",U32_V0, True)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return MODLV23.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != MODLV23:
            raise Exception("%s is not of type %s but %s" % (id, "MODLV23", type(instance)))
        fieldId = id + ".modelName"

        if (instance.modelName != None) and (type(instance.modelName) != str):
            raise Exception("%s is not a string but a %s" % (fieldId, type(instance.modelName) ))
        fieldId = id + ".flags"

        if (type(instance.flags) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".sequences"

        if (type(instance.sequences) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "SEQSV1", type(instance.sequences)))
        for itemIndex, item in enumerate(instance.sequences):
            SEQSV1.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".sequenceTransformationCollections"

        if (type(instance.sequenceTransformationCollections) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "STC_V4", type(instance.sequenceTransformationCollections)))
        for itemIndex, item in enumerate(instance.sequenceTransformationCollections):
            STC_V4.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".sequenceTransformationGroups"

        if (type(instance.sequenceTransformationGroups) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "STG_V0", type(instance.sequenceTransformationGroups)))
        for itemIndex, item in enumerate(instance.sequenceTransformationGroups):
            STG_V0.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".unknown00"

        if (type(instance.unknown00) != float):
            raise Exception("%s is not a float" % (fieldId))
        fieldId = id + ".unknown01"

        if (type(instance.unknown01) != float):
            raise Exception("%s is not a float" % (fieldId))
        fieldId = id + ".unknown02"

        if (type(instance.unknown02) != float):
            raise Exception("%s is not a float" % (fieldId))
        fieldId = id + ".unknown03"

        if (type(instance.unknown03) != float):
            raise Exception("%s is not a float" % (fieldId))
        fieldId = id + ".sts"

        if (type(instance.sts) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "STS_V0", type(instance.sts)))
        for itemIndex, item in enumerate(instance.sts):
            STS_V0.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".bones"

        if (type(instance.bones) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "BONEV1", type(instance.bones)))
        for itemIndex, item in enumerate(instance.bones):
            BONEV1.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".numberOfBonesToCheckForSkin"

        if (type(instance.numberOfBonesToCheckForSkin) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".vFlags"

        if (type(instance.vFlags) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".vertices"

        if (type(instance.vertices) != bytearray):
            raise Exception("%s is not a bytearray but a %s" % (fieldId, type(instance.vertices)))
        fieldId = id + ".divisions"

        if (type(instance.divisions) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "DIV_V2", type(instance.divisions)))
        for itemIndex, item in enumerate(instance.divisions):
            DIV_V2.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".boneLookup"
        if (type(instance.boneLookup) != list):
            raise Exception("%s is not a list of integers" % (fieldId))
        for itemIndex, item in enumerate(instance.boneLookup):
            itemId = "%s[%d]" % (fieldId, itemIndex)
            if type(item) != int: 
                raise Exception("%s is not an integer" % (itemId))
            if (item < 0) or (item > 131071):
                raise Exception("%s has value %d which is not in range [0, 131071]"  % (itemId, item))
        fieldId = id + ".boundings"

        BNDSV0.validateInstance(instance.boundings, fieldId)
        fieldId = id + ".maybeBoundingsFlags"

        if (type(instance.maybeBoundingsFlags) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".unknown04"

        if (type(instance.unknown04) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".unknown05"

        if (type(instance.unknown05) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".unknown06"

        if (type(instance.unknown06) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".unknown07"

        if (type(instance.unknown07) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".unknown08"

        if (type(instance.unknown08) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".unknown09"

        if (type(instance.unknown09) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".unknown11"

        if (type(instance.unknown11) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".unknown12"

        if (type(instance.unknown12) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".unknown13"

        if (type(instance.unknown13) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".unknown14"

        if (type(instance.unknown14) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".unknown15"

        if (type(instance.unknown15) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".unknown16"

        if (type(instance.unknown16) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".unknown17"

        if (type(instance.unknown17) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".unknown18"

        if (type(instance.unknown18) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".unknown19"

        if (type(instance.unknown19) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".attachmentPoints"

        if (type(instance.attachmentPoints) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "ATT_V1", type(instance.attachmentPoints)))
        for itemIndex, item in enumerate(instance.attachmentPoints):
            ATT_V1.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".attachmentPointAddons"
        if (type(instance.attachmentPointAddons) != list):
            raise Exception("%s is not a list of integers" % (fieldId))
        for itemIndex, item in enumerate(instance.attachmentPointAddons):
            itemId = "%s[%d]" % (fieldId, itemIndex)
            if type(item) != int: 
                raise Exception("%s is not an integer" % (itemId))
            if (item < 0) or (item > 131071):
                raise Exception("%s has value %d which is not in range [0, 131071]"  % (itemId, item))
        fieldId = id + ".lights"

        if (type(instance.lights) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "LITEV7", type(instance.lights)))
        for itemIndex, item in enumerate(instance.lights):
            LITEV7.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".shbxData"

        if (type(instance.shbxData) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "SHBXV0", type(instance.shbxData)))
        for itemIndex, item in enumerate(instance.shbxData):
            SHBXV0.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".cameras"

        if (type(instance.cameras) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "CAM_V3", type(instance.cameras)))
        for itemIndex, item in enumerate(instance.cameras):
            CAM_V3.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".d"
        if (type(instance.d) != list):
            raise Exception("%s is not a list of integers" % (fieldId))
        for itemIndex, item in enumerate(instance.d):
            itemId = "%s[%d]" % (fieldId, itemIndex)
            if type(item) != int: 
                raise Exception("%s is not an integer" % (itemId))
            if (item < 0) or (item > 131071):
                raise Exception("%s has value %d which is not in range [0, 131071]"  % (itemId, item))
        fieldId = id + ".materialReferences"

        if (type(instance.materialReferences) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "MATMV0", type(instance.materialReferences)))
        for itemIndex, item in enumerate(instance.materialReferences):
            MATMV0.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".standardMaterials"

        if (type(instance.standardMaterials) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "MAT_V15", type(instance.standardMaterials)))
        for itemIndex, item in enumerate(instance.standardMaterials):
            MAT_V15.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".displacementMaterials"

        if (type(instance.displacementMaterials) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "DIS_V4", type(instance.displacementMaterials)))
        for itemIndex, item in enumerate(instance.displacementMaterials):
            DIS_V4.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".compositeMaterials"

        if (type(instance.compositeMaterials) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "CMP_V2", type(instance.compositeMaterials)))
        for itemIndex, item in enumerate(instance.compositeMaterials):
            CMP_V2.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".terrainMaterials"

        if (type(instance.terrainMaterials) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "TER_V0", type(instance.terrainMaterials)))
        for itemIndex, item in enumerate(instance.terrainMaterials):
            TER_V0.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".volumeMaterials"

        if (type(instance.volumeMaterials) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "VOL_V0", type(instance.volumeMaterials)))
        for itemIndex, item in enumerate(instance.volumeMaterials):
            VOL_V0.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".unknownMaybeRef0"

        if (type(instance.unknownMaybeRef0) != list) or (len(instance.unknownMaybeRef0) != 0):
            raise Exception("%s is not an empty list" % (fieldId))
        fieldId = id + ".crepData"

        if (type(instance.crepData) != list) or (len(instance.crepData) != 0):
            raise Exception("%s is not an empty list" % (fieldId))
        fieldId = id + ".particles"

        if (type(instance.particles) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "PAR_V12", type(instance.particles)))
        for itemIndex, item in enumerate(instance.particles):
            PAR_V12.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".particleCopies"

        if (type(instance.particleCopies) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "PARCV0", type(instance.particleCopies)))
        for itemIndex, item in enumerate(instance.particleCopies):
            PARCV0.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".ribData"

        if (type(instance.ribData) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "RIB_V6", type(instance.ribData)))
        for itemIndex, item in enumerate(instance.ribData):
            RIB_V6.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".projData"

        if (type(instance.projData) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "PROJV4", type(instance.projData)))
        for itemIndex, item in enumerate(instance.projData):
            PROJV4.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".forData"

        if (type(instance.forData) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "FOR_V1", type(instance.forData)))
        for itemIndex, item in enumerate(instance.forData):
            FOR_V1.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".wrpData"

        if (type(instance.wrpData) != list) or (len(instance.wrpData) != 0):
            raise Exception("%s is not an empty list" % (fieldId))
        fieldId = id + ".unknownMaybeRef1"

        if (type(instance.unknownMaybeRef1) != list) or (len(instance.unknownMaybeRef1) != 0):
            raise Exception("%s is not an empty list" % (fieldId))
        fieldId = id + ".phrbData"

        if (type(instance.phrbData) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "PHRBV2", type(instance.phrbData)))
        for itemIndex, item in enumerate(instance.phrbData):
            PHRBV2.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".unknownMaybeRef2"

        if (type(instance.unknownMaybeRef2) != list) or (len(instance.unknownMaybeRef2) != 0):
            raise Exception("%s is not an empty list" % (fieldId))
        fieldId = id + ".unknownMaybeRef3"

        if (type(instance.unknownMaybeRef3) != list) or (len(instance.unknownMaybeRef3) != 0):
            raise Exception("%s is not an empty list" % (fieldId))
        fieldId = id + ".unknownMaybeRef4"

        if (type(instance.unknownMaybeRef4) != list) or (len(instance.unknownMaybeRef4) != 0):
            raise Exception("%s is not an empty list" % (fieldId))
        fieldId = id + ".ikjtData"

        if (type(instance.ikjtData) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "IKJTV0", type(instance.ikjtData)))
        for itemIndex, item in enumerate(instance.ikjtData):
            IKJTV0.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".unknownMaybeRef5"

        if (type(instance.unknownMaybeRef5) != list) or (len(instance.unknownMaybeRef5) != 0):
            raise Exception("%s is not an empty list" % (fieldId))
        fieldId = id + ".patuData"

        if (type(instance.patuData) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "PATUV4", type(instance.patuData)))
        for itemIndex, item in enumerate(instance.patuData):
            PATUV4.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".trgdData"

        if (type(instance.trgdData) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "TRGDV0", type(instance.trgdData)))
        for itemIndex, item in enumerate(instance.trgdData):
            TRGDV0.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".absoluteInverseBoneRestPositions"

        if (type(instance.absoluteInverseBoneRestPositions) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "IREFV0", type(instance.absoluteInverseBoneRestPositions)))
        for itemIndex, item in enumerate(instance.absoluteInverseBoneRestPositions):
            IREFV0.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".unknown32"

        if (type(instance.unknown32) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".unknown34"

        if (type(instance.unknown34) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".matrix"

        Matrix44.validateInstance(instance.matrix, fieldId)
        fieldId = id + ".unknown35"

        if (type(instance.unknown35) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".unknown36"

        if (type(instance.unknown36) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".unknown37"

        if (type(instance.unknown37) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".unknown38"

        if (type(instance.unknown38) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".unknown39"

        if (type(instance.unknown39) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".unknown40"

        if (type(instance.unknown40) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".unknown41"

        if (type(instance.unknown41) != float):
            raise Exception("%s is not a float" % (fieldId))
        fieldId = id + ".unknown42"

        if (type(instance.unknown42) != float):
            raise Exception("%s is not a float" % (fieldId))
        fieldId = id + ".unknown43"

        if (type(instance.unknown43) != float):
            raise Exception("%s is not a float" % (fieldId))
        fieldId = id + ".SSGS"

        if (type(instance.SSGS) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "SSGSV1", type(instance.SSGS)))
        for itemIndex, item in enumerate(instance.SSGS):
            SSGSV1.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".attachmentVolumes"

        if (type(instance.attachmentVolumes) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "ATVLV0", type(instance.attachmentVolumes)))
        for itemIndex, item in enumerate(instance.attachmentVolumes):
            ATVLV0.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".attachmentVolumesAddon0"
        if (type(instance.attachmentVolumesAddon0) != list):
            raise Exception("%s is not a list of integers" % (fieldId))
        for itemIndex, item in enumerate(instance.attachmentVolumesAddon0):
            itemId = "%s[%d]" % (fieldId, itemIndex)
            if type(item) != int: 
                raise Exception("%s is not an integer" % (itemId))
            if (item < 0) or (item > 131071):
                raise Exception("%s has value %d which is not in range [0, 131071]"  % (itemId, item))
        fieldId = id + ".attachmentVolumesAddon1"
        if (type(instance.attachmentVolumesAddon1) != list):
            raise Exception("%s is not a list of integers" % (fieldId))
        for itemIndex, item in enumerate(instance.attachmentVolumesAddon1):
            itemId = "%s[%d]" % (fieldId, itemIndex)
            if type(item) != int: 
                raise Exception("%s is not an integer" % (itemId))
            if (item < 0) or (item > 131071):
                raise Exception("%s has value %d which is not in range [0, 131071]"  % (itemId, item))
        fieldId = id + ".bbscData"

        if (type(instance.bbscData) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "BBSCV0", type(instance.bbscData)))
        for itemIndex, item in enumerate(instance.bbscData):
            BBSCV0.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))
        fieldId = id + ".tmdData"

        if (type(instance.tmdData) != list) or (len(instance.tmdData) != 0):
            raise Exception("%s is not an empty list" % (fieldId))
        fieldId = id + ".uniqueUnknownNumber"

        if (type(instance.uniqueUnknownNumber) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".unknown45"
        if (type(instance.unknown45) != list):
            raise Exception("%s is not a list of integers" % (fieldId))
        for itemIndex, item in enumerate(instance.unknown45):
            itemId = "%s[%d]" % (fieldId, itemIndex)
            if type(item) != int: 
                raise Exception("%s is not an integer" % (itemId))
            if (item < 0) or (item > 8589934591):
                raise Exception("%s has value %d which is not in range [0, 8589934591]"  % (itemId, item))


class MD34V11:
    """Header of a M3 file: Can be found at the start of the file."""
    fullName = "MD34V11"
    tagName = "MD34"
    tagVersion = 11
    size = 24
    structFormat = struct.Struct("<4sII12s")
    fields = ["tag", "indexOffset", "indexSize", "model"]

    def __setattr__(self, name, value):
        if name in ["tag", "indexOffset", "indexSize", "model"]:
            object.__setattr__(self, name, value)
        else:
            raise NoSuchAttributeException(name)
    
    def __str__(self):
        s = "{"
        first = True
        for key in ["tag", "indexOffset", "indexSize", "model"]:
            if first:
                first = False
            else:
                s += ","
            s += key + ":" + str(self.__dict__[key])
        s += "}"
        return s
    
    def resolveReferences(self, sections):
        self.model = resolveRef(self.model,sections,MODLV23,"MD34V11.model")


    @staticmethod
    def resolveReferencesOfOneOrMore(oneOrMore, sections):
        if oneOrMore.__class__ == [].__class__:
            for object in oneOrMore:
                object.resolveReferences(sections) 
        else:
            oneOrMore.resolveReferences(sections)

    def introduceIndexReferences(self, indexMaker):
        indexReference = indexMaker.getIndexReferenceTo(self.model, Reference, MODLV23)
        MODLV23.introduceIndexReferencesForOneOrMore(self.model,  indexMaker)
        self.model = indexReference


    @staticmethod
    def introduceIndexReferencesForOneOrMore(object, indexMaker):
        if object.__class__ == MD34IndexEntry:
            return # nothing to do (object was reachable trough 2 paths)
        if object.__class__ == [].__class__:
            for o in object:
                o.introduceIndexReferences(indexMaker) 
        else:
            object.introduceIndexReferences(indexMaker)

    def __init__(self, readable = None, rawBytes = None):
        if readable != None:
            assert MD34V11.size == MD34V11.structFormat.size
            rawBytes = readable.read(MD34V11.size)
        if rawBytes != None:
            l = MD34V11.structFormat.unpack(rawBytes)
            self.tag = unpackTag(l[0])
            self.indexOffset = l[1]
            self.indexSize = l[2]
            self.model = Reference(rawBytes=l[3])
        if (readable == None) and (rawBytes == None):
            self.model = MODLV23.createEmptyArray()
            pass
    @staticmethod
    def createInstances(rawBytes, count):
        list = []
        startOffset = 0
        stopOffset = startOffset + MD34V11.size
        for i in range(count):
            list.append(MD34V11(rawBytes=rawBytes[startOffset:stopOffset]));
            startOffset = stopOffset
            stopOffset += MD34V11.size
        return list
    
    def toBytes(self):
        return MD34V11.structFormat.pack(packTag(self.tag), self.indexOffset, self.indexSize, self.model.toBytes())
    
    @staticmethod
    def rawBytesForOneOrMore(oneOrMore):
        if oneOrMore.__class__ == [].__class__:
            list = oneOrMore
        else:
            list = [oneOrMore]
        rawBytes = bytearray(MD34V11.bytesRequiredForOneOrMore(oneOrMore))
        offset = 0
        nextOffset = MD34V11.size
        for object in list:
            rawBytes[offset:nextOffset] = object.toBytes()
            offset = nextOffset
            nextOffset += MD34V11.size
        return rawBytes
    
    @staticmethod
    def countOneOrMore(object):
        if object.__class__ == [].__class__:
            return len(object)
        else:
            return 1
    
    @staticmethod
    def bytesRequiredForOneOrMore(object):
        return MD34V11.countOneOrMore(object) * MD34V11.size
    
    @staticmethod
    def createEmptyArray():
        return []
    
    fieldToBitMaskMapMap = {"model": {}, "tag": {}, "indexSize": {}, "indexOffset": {}}
    
    def getNamedBit(self, field, bitName):
        mask = MD34V11.fieldToBitMaskMapMap[field][bitName]
        return ((getattr(self, field) & mask) != 0)
    
    def setNamedBit(self, field, bitName, value):
        mask = MD34V11.fieldToBitMaskMapMap[field][bitName]
        fieldValue = getattr(self, field)
        if value:
            setattr(self, field, fieldValue | mask)
        else:
            if (fieldValue & mask) != 0:
                setattr(self, field,  fieldValue ^ mask)
    
    def getBitNameMaskPairs(self, field):
        return MD34V11.fieldToBitMaskMapMap[field].items()
    
    fieldToTypeInfoMap = {"tag":FieldTypeInfo("tag",None, False), "indexOffset":FieldTypeInfo("uint32",None, False), "indexSize":FieldTypeInfo("uint32",None, False), "model":FieldTypeInfo("MODLV23",MODLV23, True)}
    @staticmethod
    def getFieldTypeInfo(fieldName):
        return MD34V11.fieldToTypeInfoMap[fieldName]
    
    @staticmethod
    def validateInstance(instance, id):
        if type(instance) != MD34V11:
            raise Exception("%s is not of type %s but %s" % (id, "MD34V11", type(instance)))
        fieldId = id + ".tag"
        if (type(instance.tag) != str) or (len(instance.tag) != 4):
            raise Exception("%s is not a string with 4 characters" % (fieldId))
        fieldId = id + ".indexOffset"

        if (type(instance.indexOffset) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".indexSize"

        if (type(instance.indexSize) != int):
            raise Exception("%s is not an int" % (fieldId))
        fieldId = id + ".model"

        if (type(instance.model) != list):
            raise Exception("%s is not a list of %s but a %s" % (fieldId, "MODLV23", type(instance.model)))
        for itemIndex, item in enumerate(instance.model):
            MODLV23.validateInstance(item, "%s[%d]" % (fieldId, itemIndex))


structMap = {"Reference":Reference,"SmallReference":SmallReference,"VEC2V0":VEC2V0,"VEC3V0":VEC3V0,"VEC4V0":VEC4V0,"QUATV0":QUATV0,"Matrix44":Matrix44,"Vector4As4uint8":Vector4As4uint8,"Vector2As2int16":Vector2As2int16,"COLV0":COLV0,"BNDSV0":BNDSV0,"AnimationReferenceHeader":AnimationReferenceHeader,"Vector3AnimationReference":Vector3AnimationReference,"Vector2AnimationReference":Vector2AnimationReference,"QuaternionAnimationReference":QuaternionAnimationReference,"UInt32AnimationReference":UInt32AnimationReference,"UInt16AnimationReference":UInt16AnimationReference,"Int16AnimationReference":Int16AnimationReference,"FloatAnimationReference":FloatAnimationReference,"ColorAnimationReference":ColorAnimationReference,"BNDSV0AnimationReference":BNDSV0AnimationReference,"REALV0":REALV0,"CHARV0":CHARV0,"U8__V0":U8__V0,"I16_V0":I16_V0,"U16_V0":U16_V0,"I32_V0":I32_V0,"U32_V0":U32_V0,"MD34IndexEntry":MD34IndexEntry,"VertexFormat0x182007d":VertexFormat0x182007d,"VertexFormat0x186007d":VertexFormat0x186007d,"VertexFormat0x18e007d":VertexFormat0x18e007d,"VertexFormat0x19e007d":VertexFormat0x19e007d,"EVNTV1":EVNTV1,"FLAGV0":FLAGV0,"SDEVV0":SDEVV0,"SD2VV0":SD2VV0,"SD3VV0":SD3VV0,"SDR3V0":SDR3V0,"SDCCV0":SDCCV0,"SDS6V0":SDS6V0,"SDU6V0":SDU6V0,"SD4QV0":SD4QV0,"SDFGV0":SDFGV0,"SDMBV0":SDMBV0,"BONEV1":BONEV1,"STC_V4":STC_V4,"SEQSV1":SEQSV1,"STG_V0":STG_V0,"STS_V0":STS_V0,"IREFV0":IREFV0,"REGNV3":REGNV3,"BAT_V1":BAT_V1,"MSECV1":MSECV1,"DIV_V2":DIV_V2,"ATT_V1":ATT_V1,"LITEV7":LITEV7,"MATMV0":MATMV0,"PATUV4":PATUV4,"TRGDV0":TRGDV0,"LAYRV22":LAYRV22,"MAT_V15":MAT_V15,"DIS_V4":DIS_V4,"CMS_V0":CMS_V0,"CMP_V2":CMP_V2,"TER_V0":TER_V0,"VOL_V0":VOL_V0,"PAR_V12":PAR_V12,"PARCV0":PARCV0,"PROJV4":PROJV4,"FOR_V1":FOR_V1,"PHSHV1":PHSHV1,"PHRBV2":PHRBV2,"SSGSV1":SSGSV1,"ATVLV0":ATVLV0,"BBSCV0":BBSCV0,"SRIBV0":SRIBV0,"RIB_V6":RIB_V6,"IKJTV0":IKJTV0,"SHBXV0":SHBXV0,"CAM_V3":CAM_V3,"MODLV23":MODLV23,"MD34V11":MD34V11}


def resolveAllReferences(list, sections):
    ListType = type([])
    for sublist in list:
        if type(sublist) == ListType:
            for entry in sublist:
                entry.resolveReferences(sections)
    
def loadSections(filename):
    source = open(filename, "rb")
    try:
        header = MD34V11(source);
        source.seek(header.indexOffset)
        sections = []
        for i in range(header.indexSize):
            section = Section()
            section.indexEntry = MD34IndexEntry(source)
            sections.append(section)
        
        offsets = []
        for section in sections:
            indexEntry = section.indexEntry
            offsets.append(indexEntry.offset)
        offsets.append(header.indexOffset)
        offsets.sort()
        previousOffset = offsets[0]
        offsetToSizeMap = {}
        for offset in offsets[1:]:
            offsetToSizeMap[previousOffset] = offset - previousOffset
            previousOffset = offset
        
        unknownSections = 0
        for section in sections:
            indexEntry = section.indexEntry
            className = indexEntry.tag + "V" + str(indexEntry.version)
            source.seek(indexEntry.offset)
            numberOfBytes = offsetToSizeMap[indexEntry.offset]
            section.rawBytes = source.read(numberOfBytes)
            if className in structMap:
                section.contentClass = structMap[className]
                section.determineContentField()
            else:
                guessedUnusedSectionBytes = 0
                for i in range (1,16):
                    if section.rawBytes[len(section.rawBytes)-i] == 0xaa:
                        guessedUnusedSectionBytes += 1
                    else:
                        break
                guessedBytesPerEntry = float(len(section.rawBytes) - guessedUnusedSectionBytes) / indexEntry.repetitions
                message = "ERROR: Unknown section at offset %s with tag=%s version=%s repetitions=%s sectionLengthInBytes=%s guessedUnusedSectionBytes=%s guessedBytesPerEntry=%s\n" % (indexEntry.offset, indexEntry.tag, indexEntry.version, indexEntry.repetitions, len(section.rawBytes),guessedUnusedSectionBytes,guessedBytesPerEntry )
                stderr.write(message)
                unknownSections += 1
        if unknownSections != 0:
            raise Exception("There were %s unknown sections" % unknownSections)
    finally:
        source.close()
    return sections

def resolveReferencesOfSections(sections):
    for section in sections:
        section.resolveReferences(sections)

def checkThatAllSectionsGotReferenced(sections):
    numberOfUnreferencedSections = 0
    for sectionIndex, section in enumerate(sections):

        if (section.timesReferenced == 0) and (sectionIndex != 0):
            numberOfUnreferencedSections += 1
            stderr.write("WARNING: %sV%s (%d repetitions) got %d times referenced\n" % (section.indexEntry.tag, section.indexEntry.version, section.indexEntry.repetitions , section.timesReferenced))
            reference = Reference()
            reference.entries = section.indexEntry.repetitions
            reference.index = sectionIndex
            reference.flags = 0
            bytesToSearch = reference.toBytes()
            possibleReferences = 0
            for sectionToCheck in sections:
                positionInSection = sectionToCheck.rawBytes.find(bytesToSearch)
                if positionInSection != -1:
                    possibleReferences += 1
                    stderr.write("  -> Found a reference at offset %d in a section of type %sV%s\n" % (positionInSection, sectionToCheck.indexEntry.tag,sectionToCheck.indexEntry.version)) 
            if possibleReferences == 0:
                bytesToSearch = bytesToSearch[0:-4]
                for sectionToCheck in sections:
                    positionInSection = sectionToCheck.rawBytes.find(bytesToSearch)
                    if positionInSection != -1:
                        flagBytes = sectionToCheck.rawBytes[positionInSection+8:positionInSection+12]
                        flagsAsHex = byteDataToHex(flagBytes)
                        stderr.write("  -> Found maybe a reference at offset %d in a section of type %sV%s with flag %s\n" % (positionInSection, sectionToCheck.indexEntry.tag,sectionToCheck.indexEntry.version, flagsAsHex)) 


    if numberOfUnreferencedSections > 0:
        raise Exception("Unable to load all data: There were %d unreferenced sections. View log for details" % numberOfUnreferencedSections)

def loadModel(filename):
    sections = loadSections(filename)
    resolveReferencesOfSections(sections)
    checkThatAllSectionsGotReferenced(sections)
    header = sections[0].content[0]
    model = header.model[0]
    MODLV23.validateInstance(model,"model")
    return model

class IndexReferenceSourceAndSectionListMaker:
    """ Creates a list of sections which are needed to store the objects for which index references are requested"""
    def __init__(self):
        self.objectsIdToIndexReferenceMap = {}
        self.offset = 0
        self.nextFreeIndexPosition = 0
        self.sections = []
    
    def getIndexReferenceTo(self, objectToSave, referenceClass, objectClass):
        if id(objectToSave) in self.objectsIdToIndexReferenceMap.keys():
            return self.objectsIdToIndexReferenceMap[id(objectToSave)]
        
        if objectClass == None:
            repetitions = 0
        else:
            repetitions = objectClass.countOneOrMore(objectToSave)
        
        indexReference = referenceClass()
        indexReference.entries = repetitions
        indexReference.index = self.nextFreeIndexPosition
        if (referenceClass == Reference):
            indexReference.flags = 0
        
        if (repetitions > 0):
            indexEntry = MD34IndexEntry()
            indexEntry.tag = objectClass.tagName
            indexEntry.offset = self.offset
            indexEntry.repetitions = repetitions
            indexEntry.version = objectClass.tagVersion
            
            section = Section()
            section.indexEntry = indexEntry
            section.content = objectToSave
            section.contentClass = structMap[("%sV%s" % (indexEntry.tag, indexEntry.version))]
            self.sections.append(section)
            self.objectsIdToIndexReferenceMap[id(objectToSave)] = indexReference
            totalBytes = objectClass.bytesRequiredForOneOrMore(objectToSave)
            totalBytes = increaseToValidSectionSize(totalBytes)
            self.offset += totalBytes
            self.nextFreeIndexPosition += 1
        return indexReference
    
    
def modelToSections(model):
    header = MD34V11()
    header.tag = "MD34"
    header.model = model
    
    indexMaker = IndexReferenceSourceAndSectionListMaker()
    indexMaker.getIndexReferenceTo([header], Reference ,MD34V11)
    header.introduceIndexReferences(indexMaker)
    sections = indexMaker.sections
    header.indexOffset = indexMaker.offset
    header.indexSize = len(sections)

    for section in sections:
        section.determineFieldRawBytes()
    return sections

def saveSections(sections, filename):
    fileObject = open(filename, "w+b")
    try:
        previousSection = None
        for section in sections:
            if section.indexEntry.offset != fileObject.tell():
                raise Exception("Section length problem: Section with index entry %(previousIndexEntry)s has length %(previousLength)s and gets followed by section with index entry %(currentIndexEntry)s" % {"previousIndexEntry":previousSection.indexEntry,"previousLength":len(previousSection.rawBytes),"currentIndexEntry":section.indexEntry} )
            fileObject.write(section.rawBytes)
            previousSection = section
        header = sections[0].content[0]
        if fileObject.tell() != header.indexOffset:
            raise Exception("Not at expected write position %s after writing sections, but %s"%(header.indexOffset, fileObject.tell()))
        for section in sections:
            fileObject.write(section.indexEntry.toBytes())
    finally:
        fileObject.close()
        
def saveAndInvalidateModel(model, filename):
    '''Do not use the model object after calling this method since it gets modified'''
    MODLV23.validateInstance(model,"model")
    sections = modelToSections(model)
    saveSections(sections, filename)


