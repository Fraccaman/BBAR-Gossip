import aiopubsub
import logwood

from src.utils.Singleton import Singleton


class PubSub(metaclass=Singleton):

    def __init__(self):
        logwood.basic_config()
        self.hub = aiopubsub.Hub()
        self.publisher = aiopubsub.Publisher(self.hub, prefix=aiopubsub.Key('peer'))
        self.subscriber = aiopubsub.Subscriber(self.hub, 'peer_id')

        sub_key = aiopubsub.Key('peer', '*')
        self.subscriber.subscribe(sub_key)

    @staticmethod
    def get_publisher_instance():
        return PubSub().publisher

    @staticmethod
    def get_subscriber_instance():
        return PubSub().subscriber

    @staticmethod
    def broadcast_epoch_time(epoch_time):
        return PubSub().get_publisher_instance().publish(aiopubsub.Key('peer', 'epoch'), epoch_time)
