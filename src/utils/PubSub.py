import aiopubsub
import logwood

from src.utils.Singleton import Singleton


class PubSub(metaclass=Singleton):

    def __init__(self):
        logwood.basic_config()
        self.hub = aiopubsub.Hub()
        self.publisher = aiopubsub.Publisher(self.hub, prefix=aiopubsub.Key('peer'))
        self.subscriber_epoch = aiopubsub.Subscriber(self.hub, 'epoch_subscr')
        self.subscriber_connection = aiopubsub.Subscriber(self.hub, 'conn_subscr')

        sub_key_epoch = aiopubsub.Key('peer', 'epoch')
        self.subscriber_epoch.subscribe(sub_key_epoch)

        sub_key_conn = aiopubsub.Key('peer', 'connection')
        self.subscriber_connection.subscribe(sub_key_conn)

    @staticmethod
    def get_publisher_instance():
        return PubSub().publisher

    @staticmethod
    def get_subscriber_epoch_instance():
        return PubSub().subscriber_epoch

    @staticmethod
    def get_subscriber_conn_instance():
        return PubSub().subscriber_connection

    @staticmethod
    def broadcast_epoch_time(epoch_time):
        return PubSub().get_publisher_instance().publish(aiopubsub.Key('epoch'), epoch_time)

    @staticmethod
    def broadcast_new_connection(address):
        return PubSub().get_publisher_instance().publish(aiopubsub.Key('connection'), address)

    @staticmethod
    async def remove_all():
        await PubSub().get_subscriber_conn_instance().remove_all_listeners()
        await PubSub().get_subscriber_epoch_instance().remove_all_listeners()
