import json
class Json():
    @classmethod
    def encode(cls, data):
        json.dumps(data, default=jsonDefEncoder)

    @classmethod
    def decode(cls, data):
        pass

def jsonDefEncoder(obj):
   if hasattr(obj, 'toJson'):
      return obj.toJson()
   else: 
        try:
            return json.dumps(obj)
        except:
            return obj.__dict__
