using System;
using System.ComponentModel;
using System.IO.MemoryMappedFiles;
using System.Xml;

namespace MeshApplication;
class BoneNode
{
        private float[] _coordinate;
        private float[] _pastCoordinate;
        public  float[] Coordinate
        {
            get
                {
                return  _coordinate;
                }
            set
                {
                _pastCoordinate = Coordinate;
                _coordinate = value;
                }
        }
        public float[] PastCoordinate
        {
            get
                {
                return _pastCoordinate;
                }
        }
        public int NodeVal {get;}

        public BoneNode(
            int nodeVal, 
            float[] coordinate)
        {
            NodeVal = nodeVal;
            _coordinate = coordinate;
            _pastCoordinate = coordinate;
        }

}

internal class Program
{
    private static void Main()

    {
        BoneNode[] node = new BoneNode[32];
        for (int i = 0; i < 32; i++)
        {
            node[i] = new BoneNode(i, [0, 0, 0]);

        }

        
    

        using (var mmf = MemoryMappedFile.OpenExisting("pose_basic"))
        using (var accessor = mmf.CreateViewAccessor())
        {
            int Calcheck = 0;
            int Calibration = 0;
            float XSum = 0;
            float YSum = 0;
            float ZSum = 0;
            float[] coords = new float[128];
            float[] CalCord = new float[128];

            static float VChange(float a, float b)
            {
                return Math.Abs((a + b));
            }

            while (true)

            {
                float x = accessor.ReadSingle(0); // first float
                float y = accessor.ReadSingle(4); // second float
                float z = accessor.ReadSingle(8); // third float
                int currentnode = accessor.ReadInt32(12);

                Thread.Sleep(16);

            }

        }
    }
}