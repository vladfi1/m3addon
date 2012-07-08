#!/usr/bin/python3
# -*- coding: utf-8 -*-

# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

if "bpy" in locals():
    import imp

# reenable this code in each addon file to make them generate the m3.py library dynamically
#    if "generateM3Library" in locals():
#        imp.reload(generateM3Library)
#from . import generateM3Library
#generateM3Library.generateM3Library()

if "bpy" in locals():
    import imp
    if "m3" in locals():
        imp.reload(m3)
    if "shared" in locals():
        imp.reload(shared)

from . import m3
from . import shared
import bpy
import mathutils
import os.path
import random

actionTypeScene = "SCENE"
actionTypeArmature = "OBJECT"

class Exporter:
    def exportParticleSystems(self, scene, m3FileName):
        self.generatedAnimIdCounter = 0
        self.scene = scene
        self.boundingAnimId = 0x1f9bd2
        if scene.render.fps != 30:
            print("Warning: It's recommended to export models with a frame rate of 30 (current is %s)" % scene.render.fps)
        self.prepareAnimIdMaps()
        self.nameToAnimIdToAnimDataMap = {}
        for animation in scene.m3_animations:
            self.nameToAnimIdToAnimDataMap[animation.name] = {}
        self.initMaterialNameToReferenceIndexMap()
        
        model = self.createModel(m3FileName)
        m3.saveAndInvalidateModel(model, m3FileName)

    def createModel(self, m3FileName):
        model = m3.MODLV23()
        model.modelName = os.path.basename(m3FileName)
        
        self.initBones(model)
        self.initMesh(model)
        self.initMaterials(model)
        self.initCameras(model)
        self.initParticles(model)
        self.initAttachmentPoints(model)
        self.prepareAnimationEndEvents()
        self.initWithPreparedAnimationData(model)
        
        model.matrix = self.createIdentityMatrix()
        model.uniqueUnknownNumber = self.getAnimIdFor(shared.animObjectIdModel, "")
        return model
    
    def prepareAnimIdMaps(self):
        self.animIdMap = {}
        self.usedAnimIds = {self.boundingAnimId}

        for animIdData in self.scene.m3_animation_ids:
            animId = animIdData.animIdMinus2147483648 + 2147483648 
            self.animIdMap[animIdData.objectId, animIdData.animPath] = animId
            self.usedAnimIds.add(animId)
    
    def getAnimIdFor(self, objectId, animPath):
        result = self.animIdMap.get((objectId, animPath))
        if result == None:
            maxValue = 0x0fffffff
            unusedAnimId = random.randint(1, maxValue)
            while unusedAnimId in self.usedAnimIds:
                unusedAnimId = random.randint(1, maxValue)
            result = unusedAnimId
            self.animIdMap[objectId, animPath] = result
        return result
    
    def createUniqueAnimId(self):
        self.generatedAnimIdCounter += 1 # increase first since we don't want to use 0 as animation id
        return self.generatedAnimIdCounter
    
    def initBones(self, model):
        self.boneNameToBoneIndexMap = {} # map: bone name to index in model bone list
        boneNameToAbsInvRestPoseMatrix = {}

        for armatureObject in self.findArmatureObjects():
            armature = armatureObject.data 
            for blenderBoneIndex, blenderBone in enumerate(armature.bones):
                boneIndex = len(model.bones)
                boneName = blenderBone.name
                if boneName in self.boneNameToBoneIndexMap:
                    raise Exception("There are multiple bones with the name %s" % lenderBone.name)
                self.boneNameToBoneIndexMap[boneName] = boneIndex
                                
                locationAnimPath = 'pose.bones["%s"].location' % boneName
                rotationAnimPath = 'pose.bones["%s"].rotation_quaternion' % boneName
                scaleAnimPath = 'pose.bones["%s"].scale' % boneName
                
                locationAnimId = self.getAnimIdFor(shared.animObjectIdArmature, locationAnimPath)
                rotationAnimId = self.getAnimIdFor(shared.animObjectIdArmature, rotationAnimPath)
                scaleAnimId = self.getAnimIdFor(shared.animObjectIdArmature, scaleAnimPath)

                bone = m3.BONEV1()
                bone.name = boneName
                bone.flags = 0
                bone.setNamedBit("flags", "real", True)
                bone.location = m3.Vector3AnimationReference()
                bone.location.header = self.createNullAnimHeader(flags=0, animId=locationAnimId)
                bone.rotation = m3.QuaternionAnimationReference()
                bone.rotation.header = self.createNullAnimHeader(flags=0, animId=rotationAnimId)
                bone.scale = m3.Vector3AnimationReference()
                bone.scale.header = self.createNullAnimHeader(flags=0, animId=scaleAnimId)
                bone.ar1 = self.createNullUInt32AnimationReference(1)
                model.bones.append(bone)

                absRestPosMatrix = blenderBone.matrix_local    
                if blenderBone.parent != None:
                    bone.parent = self.boneNameToBoneIndexMap[blenderBone.parent.name]
                    absInvRestPoseMatrixParent = boneNameToAbsInvRestPoseMatrix[blenderBone.parent.name]
                    relRestPosMatrix = absInvRestPoseMatrixParent * absRestPosMatrix
                else:
                    bone.parent = -1
                    relRestPosMatrix = absRestPosMatrix

                poseBone = armatureObject.pose.bones[blenderBoneIndex]
                poseRotationNormalized = poseBone.rotation_quaternion.normalized()
                poseMatrix = shared.locRotScaleMatrix(poseBone.location, poseRotationNormalized, poseBone.scale)
                
                if blenderBone.parent != None:
                    leftCorrectionMatrix = shared.rotFixMatrix * relRestPosMatrix
                else:
                    leftCorrectionMatrix = relRestPosMatrix
                rightCorrectionMatrix = shared.rotFixMatrixInverted
                m3PoseMatrix = leftCorrectionMatrix * poseMatrix * rightCorrectionMatrix
                
                location, rotation, scale = m3PoseMatrix.decompose()
                bone.scale.initValue = self.createVector3FromBlenderVector(scale)
                bone.scale.nullValue = self.createVector3FromBlenderVector(scale)
                bone.rotation.initValue = self.createQuaternionFromBlenderQuaternion(rotation)
                bone.rotation.nullValue = self.createQuaternionFromBlenderQuaternion(rotation)
                bone.location.initValue = self.createVector3FromBlenderVector(location)
                bone.location.nullValue = self.createVector3FromBlenderVector(location)                

        
                animationActionTuples = self.determineAnimationActionTuplesFor(armatureObject.name, actionTypeArmature)
                for animation, action in animationActionTuples:
                    frames = self.getAllFramesOf(animation)
                    timeValuesInMS = self.allFramesToMSValues(frames)
                    xLocValues = self.getNoneOrValuesFor(action, locationAnimPath, 0, frames)
                    yLocValues = self.getNoneOrValuesFor(action, locationAnimPath, 1, frames)
                    zLocValues = self.getNoneOrValuesFor(action, locationAnimPath, 2, frames)
                    wRotValues = self.getNoneOrValuesFor(action, rotationAnimPath, 0, frames)
                    xRotValues = self.getNoneOrValuesFor(action, rotationAnimPath, 1, frames)
                    yRotValues = self.getNoneOrValuesFor(action, rotationAnimPath, 2, frames)
                    zRotValues = self.getNoneOrValuesFor(action, rotationAnimPath, 3, frames)
                    xScaValues = self.getNoneOrValuesFor(action, scaleAnimPath, 0, frames)
                    yScaValues = self.getNoneOrValuesFor(action, scaleAnimPath, 1, frames)
                    zScaValues = self.getNoneOrValuesFor(action, scaleAnimPath, 2, frames)

                    locAnimated = (xLocValues != None) or (yLocValues != None) or (zLocValues != None)
                    rotAnimated = (wRotValues != None) or (xRotValues != None) or (yRotValues != None) or (zRotValues != None)
                    scaAnimated = (xScaValues != None) or (yScaValues != None) or (zScaValues != None)
                    if locAnimated or rotAnimated or scaAnimated:
                        if xLocValues == None:
                            xLocValues = len(timeValuesInMS) * [location.x]
                        if yLocValues == None:
                            yLocValues = len(timeValuesInMS) * [location.y]
                        if zLocValues == None:
                            zLocValues = len(timeValuesInMS) * [location.z]
                                                    
                        if wRotValues == None:
                            wRotValues = len(timeValuesInMS) * [rotation.w]
                        if xRotValues == None:
                            xRotValues = len(timeValuesInMS) * [rotation.x]
                        if yRotValues == None:
                            yRotValues = len(timeValuesInMS) * [rotation.y]
                        if zRotValues == None:
                            zRotValues = len(timeValuesInMS) * [rotation.z]
                            
                        if xScaValues == None:
                            xScaValues = len(timeValuesInMS) * [scale.x]
                        if yScaValues == None:
                            yScaValues = len(timeValuesInMS) * [scale.y]
                        if zScaValues == None:
                            zScaValues = len(timeValuesInMS) * [scale.z]
                            
                        locations = []
                        rotations = []
                        scales = []
                        for xLoc, yLoc, zLoc, wRot, xRot, yRot, zRot, xSca, ySca, zSca in zip(xLocValues, yLocValues, zLocValues, wRotValues, xRotValues, yRotValues, zRotValues, xScaValues, yScaValues, zScaValues):
                            loc = mathutils.Vector((xLoc, yLoc, zLoc))
                            rot = mathutils.Quaternion((wRot, xRot, yRot, zRot)).normalized()
                            sca = mathutils.Vector((xSca, ySca, zSca))
                            poseMatrix = shared.locRotScaleMatrix(loc, rot, sca)
                            m3PoseMatrix = leftCorrectionMatrix * poseMatrix * rightCorrectionMatrix
                            loc, rot, sca = m3PoseMatrix.decompose()
                            locations.append(loc)
                            rotations.append(rot)
                            scales.append(sca)
                        
                        self.makeQuaternionsInterpolatable(rotations)                                                
                        animIdToAnimDataMap = self.nameToAnimIdToAnimDataMap[animation.name]

                        #TODO exported file size optimization: 
                        # import init pose and store it in blend file together with the corresponding animId
                        # Use it then to determine if an attribute really needs to be animated when it is constant
                        if (len(self.scene.m3_animation_ids) > 0)  or self.vectorArrayContainsNotOnly(locations, location):
                            locationTimeValuesInMS, locations = shared.simplifyVectorAnimationWithInterpolation(timeValuesInMS, locations)
                            m3Locs = self.createVector3sFromBlenderVectors(locations)
                            m3AnimBlock = m3.SD3VV0()
                            m3AnimBlock.frames = locationTimeValuesInMS
                            m3AnimBlock.flags = 0
                            m3AnimBlock.fend = self.frameToMS(animation.exlusiveEndFrame)
                            m3AnimBlock.keys = m3Locs
                            animIdToAnimDataMap[locationAnimId] = m3AnimBlock
                            bone.location.header.flags = 1
                            bone.location.header.animFlags = shared.animFlagsForAnimatedProperty

                        if (len(self.scene.m3_animation_ids) > 0)  or self.quaternionArrayContainsNotOnly(rotations, rotation):
                            rotationTimeValuesInMS, rotations = shared.simplifyQuaternionAnimationWithInterpolation(timeValuesInMS, rotations)
                            m3Rots = self.createQuaternionsFromBlenderQuaternions(rotations)
                            m3AnimBlock = m3.SD4QV0()
                            m3AnimBlock.frames = rotationTimeValuesInMS
                            m3AnimBlock.flags = 0
                            m3AnimBlock.fend = self.frameToMS(animation.exlusiveEndFrame)
                            m3AnimBlock.keys = m3Rots
                            animIdToAnimDataMap[rotationAnimId] = m3AnimBlock
                            bone.rotation.header.flags = 1
                            bone.rotation.header.animFlags = shared.animFlagsForAnimatedProperty

                        if (len(self.scene.m3_animation_ids) > 0)  or self.vectorArrayContainsNotOnly(scales, scale):
                            scaleTimeValuesInMS, scales = shared.simplifyVectorAnimationWithInterpolation(timeValuesInMS, scales)
                            m3Scas = self.createVector3sFromBlenderVectors(scales)
                            m3AnimBlock = m3.SD3VV0()
                            m3AnimBlock.frames = scaleTimeValuesInMS
                            m3AnimBlock.flags = 0
                            m3AnimBlock.fend = self.frameToMS(animation.exlusiveEndFrame)
                            m3AnimBlock.keys = m3Scas
                            animIdToAnimDataMap[scaleAnimId] = m3AnimBlock
                            bone.scale.header.flags = 1
                            bone.scale.header.animFlags = shared.animFlagsForAnimatedProperty
                       
                        bone.setNamedBit("flags", "animated", True)
                   
                        
                absRestPosMatrixFixed = absRestPosMatrix * shared.rotFixMatrixInverted
                absoluteInverseRestPoseMatrixFixed = absRestPosMatrixFixed.inverted()

                absoluteInverseBoneRestPos = self.createRestPositionFromBlender4x4Matrix(absoluteInverseRestPoseMatrixFixed)
                model.absoluteInverseBoneRestPositions.append(absoluteInverseBoneRestPos)
                boneNameToAbsInvRestPoseMatrix[blenderBone.name] = absRestPosMatrix.inverted()

    def vectorArrayContainsNotOnly(self, vectorArray, vector):
        for v in vectorArray:
            if not shared.vectorsAlmostEqual(vector, v):
                return True
        return False
        
    def quaternionArrayContainsNotOnly(self, quaternionArray, quaternion):
        for q in quaternionArray:
            if not shared.quaternionsAlmostEqual(quaternion, q):
                return True
        return False
        
    def initMaterialNameToReferenceIndexMap(self):
        self.materialNameToReferenceIndexMap = {}
        for materialReferenceIndex, materialReference in enumerate(self.scene.m3_material_references):
            self.materialNameToReferenceIndexMap[materialReference.name] = materialReferenceIndex
        
    def initMesh(self, model):
        meshObjects = list(shared.findMeshObjects(self.scene))
        
        model.setNamedBit("flags", "hasMesh", len(meshObjects) > 0)
        model.boundings = self.createAlmostEmptyBoundingsWithRadius(2.0)
            
        if len(meshObjects) == 0:
            model.numberOfBonesToCheckForSkin = 0
            model.divisions = [self.createEmptyDivision()]
            return
        
        uvCoordinatesPerVertex = 1 # Never saw a m3 model with at least 1 UV layer
        for meshObject in meshObjects:
            mesh = meshObject.data
            uvCoordinatesPerVertex = max(uvCoordinatesPerVertex, len(mesh.tessface_uv_textures))

        if uvCoordinatesPerVertex == 1:
            model.vFlags = 0x182007d  
        elif uvCoordinatesPerVertex == 2:
            model.vFlags = 0x186007d
        elif uvCoordinatesPerVertex == 3:
            model.vFlags = 0x18e007d
        elif uvCoordinatesPerVertex == 4:
            model.vFlags = 0x19e007d
        else:
            raise Exception("The m3 format seems to supports only 1-4 UV layers per mesh, not %d" % uvCoordinatesPerVertex)
        m3VertexFormatClass = m3.structMap["VertexFormat" + hex(model.vFlags)]

        division = m3.DIV_V2()
        model.divisions.append(division)
        m3Vertices = []
        for meshIndex, meshObject in enumerate(meshObjects):   
            mesh = meshObject.data
            
            firstBoneLookupIndex = len(model.boneLookup)
            staticMeshBoneName = "StaticMesh"
            boneNameToBoneLookupIndexMap = {}
            boneNamesOfArmature = set()
            if len(meshObject.modifiers) == 0:
                pass
            elif len(meshObject.modifiers) == 1 and (meshObject.modifiers[0].type == "ARMATURE"):
                modifier = meshObject.modifiers[0]
                armatureObject = modifier.object
                if armatureObject != None:
                    armature = armatureObject.data
                    for blenderBoneIndex, blenderBone in enumerate(armature.bones):
                        boneNamesOfArmature.add(blenderBone.name)
            else:
                raise Exception("Mesh must have no modifiers except single one for the armature")
                
            mesh.update(calc_tessface=True)
            firstFaceVertexIndexIndex = len(division.faces)
            firstVertexIndexIndex = len(m3Vertices)
            regionFaceVertexIndices = []
            regionVertices = []
            vertexDataTupleToIndexMap = {}
            nextVertexIndex = 0
            for blenderFace in mesh.tessfaces:
                faceRelativeVertexIndexAndBlenderVertexIndexTuples = []
                if len(blenderFace.vertices) == 3 or len(blenderFace.vertices) == 4:
                    faceRelativeVertexIndexAndBlenderVertexIndexTuples.append((0, blenderFace.vertices[0]))
                    faceRelativeVertexIndexAndBlenderVertexIndexTuples.append((1, blenderFace.vertices[1]))
                    faceRelativeVertexIndexAndBlenderVertexIndexTuples.append((2, blenderFace.vertices[2]))
                    
                    if len(blenderFace.vertices) == 4:
                        faceRelativeVertexIndexAndBlenderVertexIndexTuples.append((0, blenderFace.vertices[0]))
                        faceRelativeVertexIndexAndBlenderVertexIndexTuples.append((2, blenderFace.vertices[2]))
                        faceRelativeVertexIndexAndBlenderVertexIndexTuples.append((3, blenderFace.vertices[3]))
                    
                else:
                    raise Exception("Only the export of meshes with triangles and quads has been implemented")
                
                
                
                
                for faceRelativeVertexIndex, blenderVertexIndex in faceRelativeVertexIndexAndBlenderVertexIndexTuples:
                    blenderVertex =  mesh.vertices[blenderVertexIndex]
                    m3Vertex = m3VertexFormatClass()
                    m3Vertex.position = self.blenderToM3Vector(blenderVertex.co)
                    
                    boneWeightSlot = 0
                    for gIndex, g in enumerate(blenderVertex.groups):
                        vertexGroupIndex = g.group
                        vertexGroup = meshObject.vertex_groups[vertexGroupIndex]
                        boneIndex = self.boneNameToBoneIndexMap.get(vertexGroup.name)
                        if boneIndex != None and vertexGroup.name in boneNamesOfArmature:
                            boneLookupIndex = boneNameToBoneLookupIndexMap.get(vertexGroup.name)
                            if boneLookupIndex == None:
                                boneLookupIndex = len(model.boneLookup) - firstBoneLookupIndex
                                model.boneLookup.append(boneIndex)
                                boneNameToBoneLookupIndexMap[vertexGroup.name] = boneLookupIndex
                            bone = model.bones[boneIndex]
                            bone.setNamedBit("flags", "skinned", True)
                            boneWeight = round(g.weight * 255)
                            if boneWeight != 0:
                                if boneWeightSlot == 4:
                                    raise Exception("The m3 format supports at maximum 4 bone weights per vertex")
                                setattr(m3Vertex, "boneWeight%d" % boneWeightSlot, boneWeight)
                                setattr(m3Vertex, "boneLookupIndex%d" % boneWeightSlot, boneLookupIndex)
                                boneWeightSlot += 1
                    isStaticVertex = (boneWeightSlot == 0)
                    if isStaticVertex:                    
                        staticMeshBoneIndex = self.boneNameToBoneIndexMap.get(staticMeshBoneName)
                        if staticMeshBoneIndex == None:
                            staticMeshBoneIndex = self.addBoneWithRestPosAndReturnIndex(model, staticMeshBoneName,  realBone=True)
                            model.bones[staticMeshBoneIndex].setNamedBit("flags", "skinned", True)
                            self.boneNameToBoneIndexMap[staticMeshBoneName] = staticMeshBoneIndex
                        staticMeshLookupIndex = len(model.boneLookup)
                        model.boneLookup.append(staticMeshBoneIndex)
                        boneNameToBoneLookupIndexMap[staticMeshBoneName] = staticMeshLookupIndex
                        m3Vertex.boneWeight0 = 255
                        m3Vertex.boneLookupIndex0 = staticMeshBoneIndex
                    for uvLayerIndex in range(0,uvCoordinatesPerVertex):
                        m3AttributeName = "uv" + str(uvLayerIndex)
                        blenderAttributeName = "uv%d" % (faceRelativeVertexIndex + 1)
                        if len(mesh.tessface_uv_textures) > uvLayerIndex:
                            uvData = mesh.tessface_uv_textures[uvLayerIndex].data[blenderFace.index]
                            blenderUVCoord = getattr(uvData, blenderAttributeName)
                            m3UVCoord = self.convertBlenderToM3UVCoordinates(blenderUVCoord)
                            setattr(m3Vertex, m3AttributeName, m3UVCoord)
                        else:
                            setattr(m3Vertex, m3AttributeName, self.createM3UVVector(0.0, 0.0))

                    m3Vertex.normal = self.blenderVector3AndScaleToM3Vector4As4uint8(-blenderVertex.normal, 1.0)
                    m3Vertex.tangent = self.createVector4As4uint8FromFloats(0.0, 0.0, 0.0, 0.0)
                    v = m3Vertex
                    vertexIdList = []
                    vertexIdList.extend((v.position.x, v.position.y, v.position.z))
                    vertexIdList.extend((v.boneWeight0, v.boneWeight1, v.boneWeight2, v.boneWeight3))
                    vertexIdList.extend((v.boneLookupIndex0, v.boneLookupIndex1, v.boneLookupIndex2, v.boneLookupIndex3))
                    vertexIdList.extend((v.normal.x, v.normal.y, v.normal.z))
                    for i in range(uvCoordinatesPerVertex):
                        uvAttribute = "uv" + str(i)
                        uvVector = getattr(v, uvAttribute)
                        vertexIdList.append(uvVector.x)
                        vertexIdList.append(uvVector.y)
                    vertexIdTuple = tuple(vertexIdList)

                    vertexIndex = vertexDataTupleToIndexMap.get(vertexIdTuple)
                    if vertexIndex == None:
                        vertexIndex = nextVertexIndex
                        vertexDataTupleToIndexMap[vertexIdTuple] = vertexIndex
                        nextVertexIndex += 1
                        regionVertices.append(m3Vertex)
                        m3VertexFormatClass.validateInstance(m3Vertex, "vertex")
                    regionFaceVertexIndices.append(vertexIndex)
            
            division.faces.extend(regionFaceVertexIndices)
            m3Vertices.extend(regionVertices)
            # find a bone which hasn't a parent in the list
            rootBoneIndex = None
            exlusiveBoneLookupEnd = firstBoneLookupIndex + len(boneNameToBoneLookupIndexMap)
            indicesOfUsedBones = model.boneLookup[firstBoneLookupIndex:exlusiveBoneLookupEnd]
            rootBoneIndex = self.findRootBoneIndex(model, indicesOfUsedBones)
            rootBone = model.bones[rootBoneIndex]
            
            region = m3.REGNV3()
            region.firstVertexIndex = firstVertexIndexIndex
            region.numberOfVertices = len(regionVertices)
            region.firstFaceVertexIndexIndex = firstFaceVertexIndexIndex
            region.numberOfFaceVertexIndices = len(regionFaceVertexIndices)
            region.numberOfBones = len(boneNameToBoneLookupIndexMap)
            region.firstBoneLookupIndex = firstBoneLookupIndex
            region.numberOfBoneLookupIndices = len(boneNameToBoneLookupIndexMap)
            region.rootBoneIndex = model.boneLookup[firstBoneLookupIndex]
            division.regions.append(region)
            
            m3Object = m3.BAT_V1()
            m3Object.regionIndex = meshIndex
            
            materialReferenceIndex = self.materialNameToReferenceIndexMap.get(mesh.m3_material_name)
            if materialReferenceIndex == None:
                raise Exception("The mesh %s uses '%s' as material, but no m3 material with that name exist!" % (mesh.name, mesh.m3_material_name))
            m3Object.materialReferenceIndex = materialReferenceIndex
            
            division.objects.append(m3Object)
        
        model.vertices = m3VertexFormatClass.rawBytesForOneOrMore(m3Vertices)
        
        minV = mathutils.Vector((float("inf"), float("inf") ,float("inf")))
        maxV = mathutils.Vector((-float("inf"), -float("inf"), -float("inf")))
        #TODO case 0 vertices
        for blenderVertex in mesh.vertices:
            for i in range(3):  
                minV[i] = min(minV[i], blenderVertex.co[i])
                maxV[i] = max(maxV[i], blenderVertex.co[i])
        diffV = minV - maxV
        radius = diffV.length / 2
        division.msec.append(self.createEmptyMSec(minX=minV[0], minY=minV[1], minZ=minV[2], maxX=maxV[0], maxY=maxV[1], maxZ=maxV[2], radius=radius))
        
        numberOfBonesToCheckForSkin = 0
        for boneIndex, bone in enumerate(model.bones):
            if bone.getNamedBit("flags","skinned"):
                numberOfBonesToCheckForSkin = boneIndex + 1
        model.numberOfBonesToCheckForSkin = numberOfBonesToCheckForSkin

    
    def findRootBoneIndex(self, model, boneIndices):
        boneIndexSet = set(boneIndices)
        for boneIndex in boneIndices:
            bone = model.bones[boneIndex]
            parentIndex = bone.parent
            isRoot = True
            while parentIndex != -1:
                if parentIndex in boneIndexSet:
                    isRoot = False
                parentBone = model.bones[parentIndex]
                parentIndex = parentBone.parent
            if isRoot:
                return boneIndex
    
    def makeQuaternionsInterpolatable(self, quaternions):
        if len(quaternions) < 2:
            return
            
        previousQuaternion = quaternions[0]
        for quaternion in quaternions[1:]:
            shared.smoothQuaternionTransition(previousQuaternion=previousQuaternion, quaternionToFix=quaternion)
            previousQuaternion = quaternion
    
    def blenderVector3AndScaleToM3Vector4As4uint8(self, blenderVector3, scale):
        x = blenderVector3.x
        y = blenderVector3.y
        z = blenderVector3.z
        w = scale
        return self.createVector4As4uint8FromFloats(x, y, z, w)

    def createVector4As4uint8FromFloats(self, x, y, z, w):
        m3Vector = m3.Vector4As4uint8()
        def convert(f):
            return round((-f+1) / 2.0 * 255.0)
        m3Vector.x = convert(x)
        m3Vector.y = convert(y)
        m3Vector.z = convert(z)
        m3Vector.w = convert(w)
        return m3Vector
        
    def createM3UVVector(self, x, y):
        m3UV = m3.Vector2As2int16()
        m3UV.x = round(x * 2048) 
        m3UV.y = round((1 - y) * 2048) 
        return m3UV
        
    def convertBlenderToM3UVCoordinates(self, blenderUV):
        return self.createM3UVVector(blenderUV.x, blenderUV.y)
    
    def blenderToM3Vector(self, blenderVector3):
        return self.createVector3(blenderVector3.x, blenderVector3.y, blenderVector3.z)
    
    def addBoneWithRestPosAndReturnIndex(self, model, boneName, realBone):
        boneIndex = len(model.bones)
        bone = self.createStaticBoneAtOrigin(boneName, realBone=realBone)
        model.bones.append(bone)
        
        boneRestPos = self.createIdentityRestPosition()
        model.absoluteInverseBoneRestPositions.append(boneRestPos)
        return boneIndex

    def findArmatureObjects(self):
        for currentObject in self.scene.objects:
            if currentObject.type == 'ARMATURE':
                yield currentObject
    


    def frameToMS(self, frame):
        frameRate = self.scene.render.fps
        return round((frame / frameRate) * 1000.0)
    
    def prepareAnimationEndEvents(self):
        scene = self.scene
        for animation in scene.m3_animations:
            animIdToAnimDataMap = self.nameToAnimIdToAnimDataMap[animation.name]
            animEndId = 0x65bd3215
            animIdToAnimDataMap[animEndId] = self.createAnimationEndEvent(animation)
    
    def createAnimationEndEvent(self, animation):
        event = m3.SDEVV0()
        event.frames = [self.frameToMS(animation.exlusiveEndFrame)]
        event.flags = 1
        event.fend = self.frameToMS(animation.exlusiveEndFrame)
        event.keys = [self.createAnimationEndEventKey(animation)]
        return event
        
    def createAnimationEndEventKey(self, animation):
        event = m3.EVNTV1()
        event.name = "Evt_SeqEnd"
        event.matrix = self.createIdentityMatrix()
        return event
    
    def initWithPreparedAnimationData(self, model):
        scene = self.scene
        for animation in scene.m3_animations:
            animIdToAnimDataMap = self.nameToAnimIdToAnimDataMap[animation.name]
            animIds = list(animIdToAnimDataMap.keys())
            animIds.sort()
            
            m3Sequence = m3.SEQSV1()
            m3Sequence.animStartInMS = self.frameToMS(animation.startFrame)
            m3Sequence.animEndInMS = self.frameToMS(animation.exlusiveEndFrame)
            transferer = BlenderToM3DataTransferer(exporter=self, m3Object=m3Sequence, blenderObject=animation, animPathPrefix=None, actionOwnerName=self.scene.name, actionOwnerType=actionTypeScene)
            shared.transferAnimation(transferer)
            m3Sequence.boundingSphere = self.createAlmostEmptyBoundingsWithRadius(2)
            seqIndex = len(model.sequences)
            model.sequences.append(m3Sequence)
            
            m3SequenceTransformationGroup = m3.STG_V0()
            m3SequenceTransformationGroup.name = animation.name
            stcIndex = len(model.sequenceTransformationCollections)
            m3SequenceTransformationGroup.stcIndices = [stcIndex]
            stgIndex = len(model.sequenceTransformationGroups)
            model.sequenceTransformationGroups.append(m3SequenceTransformationGroup)
            
            m3SequenceTransformationCollection = m3.STC_V4()
            m3SequenceTransformationCollection.name = animation.name + "_full"
            m3SequenceTransformationCollection.seqIndex = seqIndex
            m3SequenceTransformationCollection.stgIndex = stgIndex
            m3SequenceTransformationCollection.animIds = list(animIds)
            for animId in animIds:
                animData = animIdToAnimDataMap[animId]
                self.addAnimDataToTransformCollection(animData, m3SequenceTransformationCollection)
            model.sequenceTransformationCollections.append(m3SequenceTransformationCollection)

            m3STS = m3.STS_V0()
            m3STS.animIds = list(animIds)
            model.sts.append(m3STS)
    
    def addAnimDataToTransformCollection(self, animData, m3SequenceTransformationCollection):
        animDataType = type(animData)
        if animDataType == m3.SDEVV0:
            sdevIndex = len(m3SequenceTransformationCollection.sdev)
            m3SequenceTransformationCollection.sdev.append(animData)
            #sdev's have animation type index 0, so sdevIndex = animRef
            animRef = sdevIndex
        elif animDataType == m3.SD2VV0:
            sd2vIndex = len(m3SequenceTransformationCollection.sd2v)
            m3SequenceTransformationCollection.sd2v.append(animData)
            animRef = 0x10000 + sd2vIndex
        elif animDataType == m3.SD3VV0:
            sd3vIndex = len(m3SequenceTransformationCollection.sd3v)
            m3SequenceTransformationCollection.sd3v.append(animData)
            animRef = 0x20000 + sd3vIndex
        elif animDataType == m3.SD4QV0:
            sd4qIndex = len(m3SequenceTransformationCollection.sd4q)
            m3SequenceTransformationCollection.sd4q.append(animData)
            animRef = 0x30000 + sd4qIndex
        elif animDataType == m3.SDCCV0:
            sdccIndex = len(m3SequenceTransformationCollection.sdcc)
            m3SequenceTransformationCollection.sdcc.append(animData)
            animRef = 0x40000 + sdccIndex
        elif animDataType == m3.SDR3V0:
            sdr3Index = len(m3SequenceTransformationCollection.sdr3)
            m3SequenceTransformationCollection.sdr3.append(animData)
            animRef = 0x50000 + sdr3Index
        elif animDataType == m3.SDS6V0:
            sds6Index = len(m3SequenceTransformationCollection.sds6)
            m3SequenceTransformationCollection.sds6.append(animData)
            animRef = 0x70000 + sds6Index
        else:
            raise Exception("Can't handle animation data of type %s yet" % animDataType)
        m3SequenceTransformationCollection.animRefs.append(animRef)

    def initCameras(self, model):
        scene = self.scene
        for cameraIndex, camera in enumerate(scene.m3_cameras):
            m3Camera = m3.CAM_V3()
            boneName = camera.name
            boneIndex = self.boneNameToBoneIndexMap.get(boneName)
            if boneIndex == None:
                boneIndex = self.addBoneWithRestPosAndReturnIndex(model, boneName, realBone=False)
            m3Camera.boneIndex = boneIndex
            animPathPrefix = "m3_cameras[%s]." % cameraIndex
            transferer = BlenderToM3DataTransferer(exporter=self, m3Object=m3Camera, blenderObject=camera, animPathPrefix=animPathPrefix, actionOwnerName=self.scene.name, actionOwnerType=actionTypeScene)
            shared.transferCamera(transferer)
            model.cameras.append(m3Camera)

    def initParticles(self, model):
        scene = self.scene
        for particleSystemIndex, particleSystem in enumerate(scene.m3_particle_systems):
            boneSuffix = particleSystem.boneSuffix
            boneName = shared.boneNameForPartileSystem(boneSuffix)
            boneIndex = self.boneNameToBoneIndexMap.get(boneName)
            if boneIndex == None:
                boneIndex = self.addBoneWithRestPosAndReturnIndex(model, boneName, realBone=False)
            m3ParticleSystem = m3.PAR_V12()
            m3ParticleSystem.bone = boneIndex
            animPathPrefix = "m3_particle_systems[%s]." % particleSystemIndex
            transferer = BlenderToM3DataTransferer(exporter=self, m3Object=m3ParticleSystem, blenderObject=particleSystem, animPathPrefix=animPathPrefix, actionOwnerName=self.scene.name, actionOwnerType=actionTypeScene)
            shared.transferParticleSystem(transferer)
            m3ParticleSystem.indexPlusHighestIndex = len(scene.m3_particle_systems) -1 + particleSystemIndex
            m3ParticleSystem.ar1 = self.createNullFloatAnimationReference(initValue=1.0, nullValue=0.0)
            model.particles.append(m3ParticleSystem)
            
            materialReferenceIndex = self.materialNameToReferenceIndexMap.get(particleSystem.materialName)
            if materialReferenceIndex == None:
                raise Exception("The particle system %s uses '%s' as material, but no m3 material with that name exist!" % (particleSystem.name, particleSystem.materialName))
            m3ParticleSystem.materialReferenceIndex = materialReferenceIndex

    def initAttachmentPoints(self, model):
        scene = self.scene
        for attachmentPointIndex, attachmentPoint in enumerate(scene.m3_attachment_points):
            boneName = attachmentPoint.boneName
            boneIndex = self.boneNameToBoneIndexMap.get(boneName)
            if boneIndex == None:
                boneIndex = self.addBoneWithRestPosAndReturnIndex(model, boneName, realBone=True)
            m3AttachmentPoint = m3.ATT_V1()
            m3AttachmentPoint.name = attachmentPoint.name
            m3AttachmentPoint.bone = boneIndex
            model.attachmentPoints.append(m3AttachmentPoint)
            model.attachmentPointAddons.append(0xffff)
            
            if attachmentPoint.volumeType != "-1":
                m3AttachmentVolume = m3.ATVLV0()
                m3AttachmentVolume.bone0 = boneIndex
                m3AttachmentVolume.bone1 = boneIndex
                m3AttachmentVolume.bone2 = boneIndex
                m3AttachmentVolume.type = int(attachmentPoint.volumeType)
                m3AttachmentVolume.size0 = attachmentPoint.volumeSize0
                m3AttachmentVolume.size1 = attachmentPoint.volumeSize1
                m3AttachmentVolume.size2 = attachmentPoint.volumeSize2
                m3AttachmentVolume.matrix = self.createIdentityMatrix()
                model.attachmentVolumes.append(m3AttachmentVolume)
                model.attachmentVolumesAddon0.append(0)
                model.attachmentVolumesAddon1.append(0)

    def toM3ColorComponent(self, blenderColorComponent):
        v = round(blenderColorComponent * 255)
        if v > 255:
            v = 255
        if v < 0:
            v = 0
        return v
    
    def toM3Color(self, blenderColor):
        color = m3.COLV0()
        color.red = self.toM3ColorComponent(blenderColor[0])
        color.green = self.toM3ColorComponent(blenderColor[1])
        color.blue = self.toM3ColorComponent(blenderColor[2])
        color.alpha = self.toM3ColorComponent(blenderColor[3])
        return color
        

    def createNullVector4As4uint8(self):
        vec = m3.Vector4As4uint8()
        vec.x = 0
        vec.y = 0
        vec.z = 0
        vec.w = 0
        return vec

    def createRestPositionFromBlender4x4Matrix(self, blenderMatrix):
        iref = m3.IREFV0()
        matrix = m3.Matrix44()
        matrix.x = self.createVector4FromBlenderVector(blenderMatrix.col[0])
        matrix.y = self.createVector4FromBlenderVector(blenderMatrix.col[1])
        matrix.z = self.createVector4FromBlenderVector(blenderMatrix.col[2])
        matrix.w = self.createVector4FromBlenderVector(blenderMatrix.col[3])
        iref.matrix = matrix
        return iref

    def createIdentityRestPosition(self):
        iref = m3.IREFV0()
        iref.matrix = self.createIdentityMatrix()
        return iref

    def createStaticBoneAtOrigin(self, name, realBone):
        m3Bone = m3.BONEV1()
        m3Bone.name = name
        m3Bone.flags = 0
        m3Bone.setNamedBit("flags", "real", realBone)
        m3Bone.parent = -1
        m3Bone.location = self.createNullVector3AnimationReference(0.0, 0.0, 0.0, initIsNullValue=True)
        m3Bone.rotation = self.createNullQuaternionAnimationReference(x=0.0, y=0.0, z=0.0, w=1.0)
        m3Bone.scale = self.createNullVector3AnimationReference(1.0, 1.0, 1.0, initIsNullValue=True)
        m3Bone.ar1 = self.createNullUInt32AnimationReference(1)
        return m3Bone

    def initMaterials(self, model):
        scene = self.scene
        
        supportedMaterialTypes = {shared.standardMaterialTypeIndex, shared.displacementMaterialTypeIndex, shared.compositeMaterialTypeIndex, shared.terrainMaterialTypeIndex, shared.volumeMaterialTypeIndex}
        for materialReference in scene.m3_material_references:
            materialType = materialReference.materialType
            if materialType in supportedMaterialTypes:
                materialIndex = materialReference.materialIndex
                model.materialReferences.append(self.createMaterialReference(materialIndex, materialType))
            else:
                raise Exception("The material list contains an unsupported material of type %s" % shared.materialNames[materialType])
        for materialIndex, material in enumerate(scene.m3_standard_materials):
            model.standardMaterials.append(self.createStandardMaterial(materialIndex, material))

        for materialIndex, material in enumerate(scene.m3_displacement_materials):
            model.displacementMaterials.append(self.createDisplacementMaterial(materialIndex, material))
        
        for materialIndex, material in enumerate(scene.m3_composite_materials):
            model.compositeMaterials.append(self.createCompositeMaterial(materialIndex, material))
        
        for materialIndex, material in enumerate(scene.m3_terrain_materials):
            model.terrainMaterials.append(self.createTerrainMaterial(materialIndex, material))

        for materialIndex, material in enumerate(scene.m3_volume_materials):
            model.volumeMaterials.append(self.createVolumeMaterial(materialIndex, material))

    def createStandardMaterial(self, materialIndex, material):
        m3Material = m3.MAT_V15()
        materialAnimPathPrefix = "m3_standard_materials[%s]." % materialIndex
        transferer = BlenderToM3DataTransferer(exporter=self, m3Object=m3Material, blenderObject=material, animPathPrefix=materialAnimPathPrefix, actionOwnerName=self.scene.name, actionOwnerType=actionTypeScene)
        shared.transferStandardMaterial(transferer)

        layerIndex = 0
        for layer, layerFieldName in zip(material.layers, shared.standardMaterialLayerFieldNames):
            animPathPrefix = materialAnimPathPrefix + ".layers[%s]." % layerIndex
            m3Layer = self.createMaterialLayer(layer, animPathPrefix)
            setattr(m3Material, layerFieldName, [m3Layer])
            layerIndex += 1

        m3Material.unknownAnimationRef1 = self.createNullUInt32AnimationReference(0)
        m3Material.unknownAnimationRef2 = self.createNullUInt32AnimationReference(0)
        return m3Material

    def createDisplacementMaterial(self, materialIndex, material):
        m3Material = m3.DIS_V4()
        materialAnimPathPrefix = "m3_displacement_materials[%s]." % materialIndex
        transferer = BlenderToM3DataTransferer(exporter=self, m3Object=m3Material, blenderObject=material, animPathPrefix=materialAnimPathPrefix, actionOwnerName=self.scene.name, actionOwnerType=actionTypeScene)
        shared.transferDisplacementMaterial(transferer)

        layerIndex = 0
        for layer, layerFieldName in zip(material.layers, shared.displacementMaterialLayerFieldNames):
            animPathPrefix = materialAnimPathPrefix + ".layers[%s]." % layerIndex
            m3Layer = self.createMaterialLayer(layer, animPathPrefix)
            setattr(m3Material, layerFieldName, [m3Layer])
            layerIndex += 1
        return m3Material

    def createCompositeMaterial(self, materialIndex, material):
        m3Material = m3.CMP_V2()
        materialAnimPathPrefix = "m3_composite_materials[%s]." % materialIndex
        transferer = BlenderToM3DataTransferer(exporter=self, m3Object=m3Material, blenderObject=material, animPathPrefix=materialAnimPathPrefix, actionOwnerName=self.scene.name, actionOwnerType=actionTypeScene)
        shared.transferCompositeMaterial(transferer)
        for sectionIndex, section in enumerate(material.sections):
            m3Section = m3.CMS_V0()
            m3Section.materialReferenceIndex = self.materialNameToReferenceIndexMap[section.name]
            sectionAnimPathPrefix = "m3_composite_materials[%s].sections[%s]." % (materialIndex, sectionIndex)
            transferer = BlenderToM3DataTransferer(exporter=self, m3Object=m3Section, blenderObject=section, animPathPrefix=sectionAnimPathPrefix, actionOwnerName=self.scene.name, actionOwnerType=actionTypeScene)
            shared.transferCompositeMaterialSection(transferer)
            m3Material.sections.append(m3Section)
            
        return m3Material

    def createTerrainMaterial(self, materialIndex, material):
        m3Material = m3.TER_V0()
        materialAnimPathPrefix = "m3_terrain_materials[%s]." % materialIndex
        transferer = BlenderToM3DataTransferer(exporter=self, m3Object=m3Material, blenderObject=material, animPathPrefix=materialAnimPathPrefix, actionOwnerName=self.scene.name, actionOwnerType=actionTypeScene)
        shared.transferTerrainMaterial(transferer)

        layerIndex = 0
        for layer, layerFieldName in zip(material.layers, shared.terrainMaterialLayerFieldNames):
            animPathPrefix = materialAnimPathPrefix + ".layers[%s]." % layerIndex
            m3Layer = self.createMaterialLayer(layer, animPathPrefix)
            setattr(m3Material, layerFieldName, [m3Layer])
            layerIndex += 1
        return m3Material

    def createVolumeMaterial(self, materialIndex, material):
        m3Material = m3.VOL_V0()
        materialAnimPathPrefix = "m3_volume_materials[%s]." % materialIndex
        transferer = BlenderToM3DataTransferer(exporter=self, m3Object=m3Material, blenderObject=material, animPathPrefix=materialAnimPathPrefix, actionOwnerName=self.scene.name, actionOwnerType=actionTypeScene)
        shared.transferVolumeMaterial(transferer)

        layerIndex = 0
        for layer, layerFieldName in zip(material.layers, shared.volumeMaterialLayerFieldNames):
            animPathPrefix = materialAnimPathPrefix + ".layers[%s]." % layerIndex
            m3Layer = self.createMaterialLayer(layer, animPathPrefix)
            setattr(m3Material, layerFieldName, [m3Layer])
            layerIndex += 1
        return m3Material

    def createMaterialLayer(self, layer, animPathPrefix):
        m3Layer = m3.LAYRV22()
        transferer = BlenderToM3DataTransferer(exporter=self, m3Object=m3Layer, blenderObject=layer, animPathPrefix=animPathPrefix, actionOwnerName=self.scene.name, actionOwnerType=actionTypeScene)
        shared.transferMaterialLayer(transferer)
        m3Layer.unknown6 = self.createNullUInt32AnimationReference(0)
        m3Layer.unknown7 = self.createNullVector2AnimationReference(0.0, 0.0, flags=0)
        m3Layer.unknown8 = self.createNullUInt16AnimationReference(0)
        m3Layer.uvOffset = self.createNullVector2AnimationReference(0.0, 0.0, flags=1)
        m3Layer.uvAngle = self.createNullVector3AnimationReference(0.0, 0.0, 0.0, flags=1, initIsNullValue=False)
        m3Layer.uvTiling = self.createNullVector2AnimationReference(1.0, 1.0, flags=1)
        m3Layer.unknown9 = self.createNullUInt32AnimationReference(0, flags=1)
        m3Layer.unknown10 = self.createNullFloatAnimationReference(1.0, flags=1)
        return m3Layer

    def createNullVector2AnimationReference(self, x, y, flags=1):
        animRef = m3.Vector2AnimationReference()
        animRef.header = self.createNullAnimHeader(flags=flags)
        animRef.initValue = self.createVector2(x, y)
        animRef.nullValue = self.createVector2(0.0, 0.0)
        return animRef
        
    def createNullVector3AnimationReference(self, x, y, z, initIsNullValue, flags=1):
        animRef = m3.Vector3AnimationReference()
        animRef.header = self.createNullAnimHeader(flags=flags)
        animRef.initValue = self.createVector3(x, y, z)
        if initIsNullValue:
            animRef.nullValue = self.createVector3(x, y, z)
        else:
            animRef.nullValue = self.createVector3(0.0, 0.0, 0.0)
        return animRef
    
    def createNullQuaternionAnimationReference(self, x=0.0, y=0.0, z=0.0, w=1.0):
        animRef = m3.QuaternionAnimationReference()
        animRef.header = self.createNullAnimHeader()
        animRef.initValue = self.createQuaternion(x=x, y=y, z=z, w=w)
        animRef.nullValue = self.createQuaternion(x=x, y=y, z=z, w=w)
        return animRef
        
    def createNullInt16AnimationReference(self, value):
        animRef = m3.Int16AnimationReference()
        animRef.header = self.createNullAnimHeader()
        animRef.initValue = value
        animRef.nullValue = 0
        return animRef
    
    def createNullUInt16AnimationReference(self, value):
        animRef = m3.UInt16AnimationReference()
        animRef.header = self.createNullAnimHeader()
        animRef.initValue = value
        animRef.nullValue = 0
        return animRef  
    
    def createNullUInt32AnimationReference(self, value, flags=0):
        animRef = m3.UInt32AnimationReference()
        animRef.header = self.createNullAnimHeader(flags = flags)
        animRef.initValue = value
        animRef.nullValue = 0
        return animRef
        
    def createNullFloatAnimationReference(self, initValue, nullValue=None, flags=1):
        if nullValue == None:
            nullValue = initValue
        animRef = m3.FloatAnimationReference()
        animRef.header = self.createNullAnimHeader(flags=flags)
        animRef.initValue = initValue
        animRef.nullValue = 0.0
        return animRef
    
    def createNullAnimHeader(self, flags=0, animId=None):
        animRefHeader = m3.AnimationReferenceHeader()
        animRefHeader.flags = flags
        animRefHeader.animFlags = 0
        if animId == None:
            animRefHeader.animId = self.createUniqueAnimId()
        else:
            animRefHeader.animId = animId
        return animRefHeader
        

    
    def createMaterialReference(self, materialIndex, materialType):
        materialReference = m3.MATMV0()
        materialReference.materialType = materialType
        materialReference.materialIndex = materialIndex
        return materialReference

    def createEmptyDivision(self):
        division = m3.DIV_V2()
        division.faces = []
        division.regions = []
        division.objects = []
        division.msec = [self.createEmptyMSec()]
        return division
    
    def createEmptyMSec(self, minX=0.0, minY=0.0, minZ=0.0, maxX=0.0, maxY=0.0, maxZ=0.0, radius=0.0):
        msec = m3.MSECV1()
        msec.boundingsAnimation = self.createDummyBoundingsAnimation(minX, minY, minZ, maxX, maxY, maxZ, radius)
        return msec
    
    def createDummyBoundingsAnimation(self, minX=0.0, minY=0.0, minZ=0.0, maxX=0.0, maxY=0.0, maxZ=0.0, radius=0.0):
        boundingsAnimRef = m3.BNDSV0AnimationReference()
        animHeader = m3.AnimationReferenceHeader()
        animHeader.flags = 0x0
        animHeader.animFlags = 0x0
        animHeader.animId = self.boundingAnimId # boudings seem to have always this id
        boundingsAnimRef.header = animHeader
        boundingsAnimRef.initValue = self.createBoundings(minX, minY, minZ, maxX, maxY, maxZ, radius)
        boundingsAnimRef.nullValue = self.createBoundings(minX, minY, minZ, maxX, maxY, maxZ, radius)
        return boundingsAnimRef
    
    def createBoundings(self, minX=0.0, minY=0.0, minZ=0.0, maxX=0.0, maxY=0.0, maxZ=0.0, radius=0.0):
        boundings = m3.BNDSV0()
        boundings.min = self.createVector3(minX, minY, minZ)
        boundings.max = self.createVector3(maxX, maxY, maxZ)
        boundings.radius = radius
        return boundings
        
    def createAlmostEmptyBoundingsWithRadius(self, r):
        boundings = m3.BNDSV0()
        boundings.min = self.createVector3(0.0,0.0,0.0)
        epsilon = 9.5367431640625e-07
        boundings.max = self.createVector3(epsilon, epsilon, epsilon)
        boundings.radius = float(r)
        return boundings

    def createVector4(self, x, y, z, w):
        v = m3.VEC4V0()
        v.x = x
        v.y = y
        v.z = z
        v.w = w
        return v
    
    def createQuaternion(self, x, y, z, w):
        q = m3.QUATV0()
        q.x = x
        q.y = y
        q.z = z
        q.w = w
        return q
    
    def createColor(self, r, g, b, a):
        color = m3.COLV0()
        color.red = self.toM3ColorComponent(r)
        color.green = self.toM3ColorComponent(g)
        color.blue = self.toM3ColorComponent(b)
        color.alpha = self.toM3ColorComponent(a)
        return color

    def createVector3(self, x, y, z):
        v = m3.VEC3V0()
        v.x = x
        v.y = y
        v.z = z
        return v
    
    def createVector2(self, x, y):
        v = m3.VEC2V0()
        v.x = x
        v.y = y
        return v
        
    def createVector3FromBlenderVector(self, blenderVector):
        return self.createVector3(blenderVector.x, blenderVector.y, blenderVector.z)
        
    def createVector3sFromBlenderVectors(self, blenderVectors):
        m3Vectors = []
        for blenderVector in blenderVectors:
            m3Vectors.append(self.createVector3FromBlenderVector(blenderVector))
        return m3Vectors

    def createVector4FromBlenderVector(self, blenderVector):
        return self.createVector4(blenderVector[0], blenderVector[1], blenderVector[2], blenderVector[3])

    def createQuaternionFromBlenderQuaternion(self, q):
        return self.createQuaternion(x=q.x, y=q.y, z=q.z, w=q.w)
    
    def createQuaternionsFromBlenderQuaternions(self, blenderQuaternions):
        m3Quaternions = []
        for blenderQuaternion in blenderQuaternions:
            m3Quaternions.append(self.createQuaternionFromBlenderQuaternion(blenderQuaternion))
        return m3Quaternions
    
    def createIdentityMatrix(self):
        matrix = m3.Matrix44()
        matrix.x = self.createVector4(1.0, 0.0, 0.0, 0.0)
        matrix.y = self.createVector4(0.0, 1.0, 0.0, 0.0)
        matrix.z = self.createVector4(0.0, 0.0, 1.0, 0.0)
        matrix.w = self.createVector4(0.0, 0.0, 0.0, 1.0)
        return matrix
        
    def determineAnimationActionTuplesFor(self, actionOwnerName, actionOwnerType):
        animationActionTuples = []
        scene = self.scene
        for animation in scene.m3_animations:
            for assignedAction in animation.assignedActions:
                if actionOwnerName == assignedAction.targetName:
                    actionName = assignedAction.actionName
                    action = bpy.data.actions.get(actionName)
                    if action == None:
                        print("Warning: The action %s was referenced by name but does no longer exist" % assignedAction.actionName)
                    else:
                        if action.id_root == actionOwnerType:
                            animationActionTuples.append((animation, action))
        return animationActionTuples

    
    
    def getAllFramesOf(self, animation):
        # end frame is inclusve in blender
        return range(animation.startFrame, animation.exlusiveEndFrame)
        
    def allFramesToMSValues(self, frames):
        timeValues = []
        for frame in frames:
            timeInMS = self.frameToMS(frame)
            timeValues.append(timeInMS)
        return timeValues
    
    def getNoneOrValuesFor(self, action, animPath, curveArrayIndex, frames):
        values = []
        curve = self.findFCurveWithPathAndIndex(action, animPath, curveArrayIndex)
        if curve == None:
            return None
        for frame in frames:
            values.append(curve.evaluate(frame))
        return values
            
    def findFCurveWithPathAndIndex(self, action, animPath, curveArrayIndex):
        for curve in action.fcurves:
            if (curve.data_path == animPath) and (curve.array_index == curveArrayIndex):
                return curve
        return None

class BlenderToM3DataTransferer:
    def __init__(self, exporter, m3Object, blenderObject, animPathPrefix,  actionOwnerName, actionOwnerType):
        self.exporter = exporter
        self.m3Object = m3Object
        self.blenderObject = blenderObject
        self.animPathPrefix = animPathPrefix
        self.actionOwnerName = actionOwnerName
        self.actionOwnerType = actionOwnerType
        self.objectIdForAnimId = shared.animObjectIdScene
        
        self.animationActionTuples = self.exporter.determineAnimationActionTuplesFor(actionOwnerName, actionOwnerType)
        
    def transferAnimatableColor(self, fieldName):
        animPath = self.animPathPrefix + fieldName
        animId = self.exporter.getAnimIdFor(self.objectIdForAnimId, animPath)
        animRef = m3.ColorAnimationReference()
        animRef.header = self.exporter.createNullAnimHeader(animId=animId)
        m3CurrentColor =  self.exporter.toM3Color(getattr(self.blenderObject, fieldName))
        animRef.initValue = m3CurrentColor
        animRef.nullValue = self.exporter.createColor(0,0,0,0)
        setattr(self.m3Object, fieldName, animRef)
        
 
        for animation, action in self.animationActionTuples:
            frames = self.exporter.getAllFramesOf(animation)
            timeValuesInMS = self.exporter.allFramesToMSValues(frames)
            redValues = self.exporter.getNoneOrValuesFor(action, animPath, 0, frames)
            greenValues = self.exporter.getNoneOrValuesFor(action, animPath, 1, frames)
            blueValues = self.exporter.getNoneOrValuesFor(action, animPath, 2, frames)
            alphaValues = self.exporter.getNoneOrValuesFor(action, animPath, 2, frames)
            if (redValues != None) or (greenValues != None) or (blueValues != None) or (alphaValues != None):
                if redValues == None:
                    redValues = len(timeValuesInMS) * [m3CurrentColor.red]
                if greenValues == None:
                    greenValues = len(timeValuesInMS) * [m3CurrentColor.green]
                if blueValues == None:
                    blueValues = len(timeValuesInMS) * [m3CurrentColor.blue]
                if alphaValues == None:
                    alphaValues = len(timeValuesInMS) * [m3CurrentColor.alpha]
                colors = []
                for (r,g,b,a) in zip(redValues, greenValues, blueValues, alphaValues):
                    color = self.exporter.createColor(r=r, g=g, b=b, a=a)
                    colors.append(color)
                
                m3AnimBlock = m3.SDCCV0()
                m3AnimBlock.frames = timeValuesInMS
                m3AnimBlock.flags = 0
                m3AnimBlock.fend = self.exporter.frameToMS(animation.exlusiveEndFrame)
                m3AnimBlock.keys = colors
                
                animIdToAnimDataMap = self.exporter.nameToAnimIdToAnimDataMap[animation.name]
                animIdToAnimDataMap[animId] = m3AnimBlock
                animRef.header.flags = 1
                animRef.header.animFlags = shared.animFlagsForAnimatedProperty
        #TODO Optimization: Remove keyframes that can be calculated by interpolation   

    def transferAnimatableSingleFloatOrInt(self, fieldName, animRefClass, animRefFlags, animDataClass, convertMethod):
        animPath = self.animPathPrefix + fieldName
        animId = self.exporter.getAnimIdFor(self.objectIdForAnimId, animPath)
        animRef = animRefClass()
        animRef.header = self.exporter.createNullAnimHeader(animId=animId)
        currentValue =  getattr(self.blenderObject, fieldName)
        animRef.initValue = currentValue
        animRef.nullValue = type(currentValue)(0)
        for animation, action in self.animationActionTuples:
            frames = self.exporter.getAllFramesOf(animation)
            timeValuesInMS = self.exporter.allFramesToMSValues(frames)
            values = self.exporter.getNoneOrValuesFor(action, animPath, 0, frames)
            if values != None:
                convertedValues = []
                for value in values:
                    convertedValues.append(convertMethod(value))
                m3AnimBlock = animDataClass()
                m3AnimBlock.frames = timeValuesInMS
                m3AnimBlock.flags = 0
                m3AnimBlock.fend = self.exporter.frameToMS(animation.exlusiveEndFrame)
                m3AnimBlock.keys = convertedValues
                
                animIdToAnimDataMap = self.exporter.nameToAnimIdToAnimDataMap[animation.name]
                animIdToAnimDataMap[animId] = m3AnimBlock
                animRef.header.flags = animRefFlags
                animRef.header.animFlags = shared.animFlagsForAnimatedProperty
        #TODO Optimization: Remove keyframes that can be calculated by interpolation
        setattr(self.m3Object, fieldName, animRef)
   
        
    def transferAnimatableFloat(self, fieldName):
        def identity(value):
            return value
        self.transferAnimatableSingleFloatOrInt(fieldName, animRefClass=m3.FloatAnimationReference, animRefFlags=1, animDataClass=m3.SDR3V0,convertMethod=identity)
        

    def transferAnimatableInt16(self, fieldName):
        def toInt16Value(value):
            return min((1<<16)-1,  max(0, round(value)))
        self.transferAnimatableSingleFloatOrInt(fieldName, animRefClass=m3.Int16AnimationReference, animRefFlags=0, animDataClass=m3.SDS6V0, convertMethod=toInt16Value)

    def transferAnimatableUInt32(self, fieldName):
        #TODO Test this method once the purpose of an animated int32 field is known
        def toUInt32Value(value):
            return min((1<<32)-1,  max(0, round(value)))
        self.transferAnimatableSingleFloatOrInt(fieldName, animRefClass=m3.UInt32AnimationReference, animRefFlags=0, animDataClass=m3.FLAGV0, convertMethod=toUInt32Value)

    def transferAnimatableVector3(self, fieldName):
        animPath = self.animPathPrefix + fieldName
        animId = self.exporter.getAnimIdFor(self.objectIdForAnimId, animPath)
        animRef = m3.Vector3AnimationReference()
        animRef.header = self.exporter.createNullAnimHeader(animId=animId)
        currentBVector =  getattr(self.blenderObject, fieldName)
        animRef.initValue = self.exporter.createVector3FromBlenderVector(currentBVector)
        animRef.nullValue = self.exporter.createVector3(0.0,0.0,0.0)
        setattr(self.m3Object, fieldName, animRef)

        for animation, action in self.animationActionTuples:
            frames = self.exporter.getAllFramesOf(animation)
            timeValuesInMS = self.exporter.allFramesToMSValues(frames)
            xValues = self.exporter.getNoneOrValuesFor(action, animPath, 0, frames)
            yValues = self.exporter.getNoneOrValuesFor(action, animPath, 1, frames)
            zValues = self.exporter.getNoneOrValuesFor(action, animPath, 2, frames)
            if (xValues != None) or (yValues != None) or (zValues != None):
                if xValues == None:
                    xValues = len(timeValuesInMS) * [currentBVector.x]
                if yValues == None:
                    yValues = len(timeValuesInMS) * [currentBVector.y]
                if zValues == None:
                    zValues = len(timeValuesInMS) * [currentBVector.z]
                vectors = []
                for (x,y,z) in zip(xValues, yValues, zValues):
                    vec = self.exporter.createVector3(x,y,z)
                    vectors.append(vec)
                
                m3AnimBlock = m3.SD3VV0()
                m3AnimBlock.frames = timeValuesInMS
                m3AnimBlock.flags = 0
                m3AnimBlock.fend = self.exporter.frameToMS(animation.exlusiveEndFrame)
                m3AnimBlock.keys = vectors
                
                animIdToAnimDataMap = self.exporter.nameToAnimIdToAnimDataMap[animation.name]
                animIdToAnimDataMap[animId] = m3AnimBlock
                animRef.header.flags = 1
                animRef.header.animFlags = shared.animFlagsForAnimatedProperty
        #TODO Optimization: Remove keyframes that can be calculated by interpolation
        
    def transferInt(self, fieldName):
        value = getattr(self.blenderObject, fieldName)
        setattr(self.m3Object, fieldName , value)
        
    def transferBoolean(self, fieldName):
        booleanValue = getattr(self.blenderObject, fieldName)
        if booleanValue:
            intValue = 1
        else:
            intValue = 0
        setattr(self.m3Object, fieldName , intValue)

    def transferBit(self, m3FieldName, bitName):
        booleanValue = getattr(self.blenderObject, bitName)
        self.m3Object.setNamedBit(m3FieldName, bitName, booleanValue)

    def transferFloat(self, fieldName):
        value = getattr(self.blenderObject, fieldName)
        setattr(self.m3Object, fieldName , value)
        
    def transferString(self, fieldName):
        value = getattr(self.blenderObject, fieldName)
        setattr(self.m3Object, fieldName , value)
        
    def transferEnum(self, fieldName):
        value = getattr(self.blenderObject, fieldName)
        setattr(self.m3Object, fieldName , int(value))

        
def exportParticleSystems(scene, filename):
    exporter = Exporter()
    shared.setAnimationWithIndexToCurrentData(scene, scene.m3_animation_index)
    exporter.exportParticleSystems(scene, filename)
