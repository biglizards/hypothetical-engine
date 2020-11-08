cdef extern from "assimp/Importer.hpp" namespace "Assimp":
    cpdef cppclass Importer:
        Importer() except +
        const aiScene* ReadFile(const char* pFile, unsigned int pFlags) except +
        const char* GetErrorString() except +

cdef extern from "assimp/scene.h":
    cdef unsigned int AI_SCENE_FLAGS_INCOMPLETE
    # assumes ASSIMP_DOUBLE_PRECISION is set
    ctypedef double ai_real

    cpdef cppclass aiVector3D:
        ai_real x, y, z

    ctypedef struct aiFace:
        unsigned int mNumIndices
        unsigned int* mIndices

    ctypedef struct aiMesh:
        unsigned int mPrimitiveTypes
        unsigned int mNumVertices
        unsigned int mNumFaces
        aiVector3D* mVertices
        aiVector3D* mNormals
        aiVector3D* mTangents
        aiVector3D* mBitangents
        aiVector3D** mTextureCoords  # [AI_MAX_NUMBER_OF_TEXTURECOORDS]
        unsigned int* mNumUVComponents
        aiFace* mFaces
        unsigned int mMaterialIndex

    ctypedef struct aiScene:
        unsigned int mFlags
        aiNode* mRootNode
        unsigned int mNumMeshes
        aiMesh** mMeshes
        unsigned int mNumMaterials
        aiMaterial** mMaterials
        unsigned int mNumAnimations
        # aiAnimation** mAnimations  # can you imagine
        unsigned int mNumTextures
        # aiTexture** mTextures
        unsigned int mNumLights
        # aiLight** mLights
        unsigned int mNumCameras
        # aiCamera** mCameras  # ok this one is never gonna happen why is that even a thing

    ctypedef struct aiNode:
        # aiString mName  # wtf is an aiString. No. Im not wrapping that.
        # aiMatrix4x4 mTransformation  # u_u' no
        aiNode* mParent
        unsigned int mNumChildren
        aiNode** mChildren
        unsigned int mNumMeshes
        unsigned int* mMeshes

    cpdef cppclass aiMaterial:
        # aiMaterialProperty** mProperties
        unsigned int mNumProperties
        unsigned int mNumAllocated
        unsigned int GetTextureCount(aiTextureType type) except +
        void GetTexture(aiTextureType type, unsigned int  index, aiString* path) except +

    cpdef cppclass aiString:
        const char* C_Str() except +

    enum aiTextureType:
        aiTextureType_NONE
        aiTextureType_DIFFUSE
        aiTextureType_SPECULAR
        aiTextureType_AMBIENT
        aiTextureType_EMISSIVE
        aiTextureType_HEIGHT
        aiTextureType_NORMALS
        aiTextureType_SHININESS
        aiTextureType_OPACITY
        aiTextureType_DISPLACEMENT
        aiTextureType_LIGHTMAP
        aiTextureType_REFLECTION
        aiTextureType_UNKNOWN

cdef extern from "assimp/postprocess.h":
    enum aiPostProcessSteps:
        aiProcess_CalcTangentSpace
        aiProcess_JoinIdenticalVertices
        aiProcess_MakeLeftHanded
        aiProcess_Triangulate
        aiProcess_RemoveComponent
        aiProcess_GenNormals
        aiProcess_GenSmoothNormals
        aiProcess_SplitLargeMeshes
        aiProcess_PreTransformVertices
        aiProcess_LimitBoneWeights
        aiProcess_ValidateDataStructure
        aiProcess_ImproveCacheLocality
        aiProcess_RemoveRedundantMaterials
        aiProcess_FixInfacingNormals
        aiProcess_SortByPType
        aiProcess_FindDegenerates
        aiProcess_FindInvalidData
        aiProcess_GenUVCoords
        aiProcess_TransformUVCoords
        aiProcess_FindInstances
        aiProcess_OptimizeMeshes
        aiProcess_OptimizeGraph
        aiProcess_FlipUVs
        aiProcess_FlipWindingOrder
        aiProcess_SplitByBoneCount
        aiProcess_Debone
        aiProcess_GlobalScale
        aiProcess_EmbedTextures
        aiProcess_ForceGenNormals
        aiProcess_DropNormals