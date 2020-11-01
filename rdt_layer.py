from segment import Segment


# #################################################################################################################### #
# RDTLayer                                                                                                             #
#                                                                                                                      #
# Description:                                                                                                         #
# The reliable data transfer (RDT) layer is used as a communication layer to resolve issues over an unreliable         #
# channel.                                                                                                             #
#                                                                                                                      #
#                                                                                                                      #
# Notes:                                                                                                               #
# This file is meant to be changed.                                                                                    #
#                                                                                                                      #
#                                                                                                                      #
# #################################################################################################################### #


class RDTLayer(object):
    # ################################################################################################################ #
    # Class Scope Variables                                                                                            #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    DATA_LENGTH = 4 # in characters                     # The length of the string data that will be sent per packet...
    FLOW_CONTROL_WIN_SIZE = 15 # in characters          # Receive window size for flow-control
    sendChannel = None
    receiveChannel = None
    dataToSend = ''
    currentIteration = 0                                # Use this for segment 'timeouts'

    countSegmentTimeouts = 0
    num_packets_sent = 0
    receivedDataList = []
    receivedAckList = []
    # Add items as needed

    # ################################################################################################################ #
    # __init__()                                                                                                       #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def __init__(self):
        self.sendChannel = None
        self.receiveChannel = None
        self.dataToSend = ''
        self.currentIteration = 0

        self.countSegmentTimeouts = 0
        self.num_packets_sent = 0
        self.receivedDataList = []
        self.receivedAckList = []

        # Add items as needed

    # ################################################################################################################ #
    # setSendChannel()                                                                                                 #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Called by main to set the unreliable sending lower-layer channel                                                 #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def setSendChannel(self, channel):
        self.sendChannel = channel

    # ################################################################################################################ #
    # setReceiveChannel()                                                                                              #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Called by main to set the unreliable receiving lower-layer channel                                               #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def setReceiveChannel(self, channel):
        self.receiveChannel = channel

    # ################################################################################################################ #
    # setDataToSend()                                                                                                  #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Called by main to set the string data to send                                                                    #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def setDataToSend(self, data):
        self.dataToSend = data

    # ################################################################################################################ #
    # getDataReceived()                                                                                                #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Called by main to get the currently received and buffered string data, in order                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def getDataReceived(self):
        # ############################################################################################################ #
        # Identify the data that has been received...
        data = ""
        for i in self.receivedDataList:
            data += i.payload

        # ############################################################################################################ #
        return data

    # ################################################################################################################ #
    # processData()                                                                                                    #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # "timeslice". Called by main once per iteration                                                                   #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def processData(self):
        self.currentIteration += 1
        self.processReceiveAndSendRespond()
        self.processSend()

    # ################################################################################################################ #
    # processSend()                                                                                                    #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Manages Segment sending tasks                                                                                    #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def processSend(self):

        # ############################################################################################################ #

        # You should pipeline segments to fit the flow-control window
        # The flow-control window is the constant RDTLayer.FLOW_CONTROL_WIN_SIZE
        # The maximum data that you can send in a segment is RDTLayer.DATA_LENGTH
        # These constants are given in # characters

        # Somewhere in here you will be creating data segments to send.
        # The data is just part of the entire string that you are trying to send.
        # The seqnum is the sequence number for the segment (in character number, not bytes)

        packet_total = int(len(self.dataToSend) / self.DATA_LENGTH)
        packet_sent = 0
        for x in range(packet_total):
            if x not in self.receivedAckList and packet_sent < 3:
                segmentSend = Segment()
                seg_start = x * self.DATA_LENGTH
                seg_end = (x + 1) * self.DATA_LENGTH

                data = self.dataToSend[seg_start:seg_end]

                # ############################################################################################################ #
                # Display sending segment
                segmentSend.setData(x, data)
                print("Sending segment: ", segmentSend.to_string())

                # Use the unreliable sendChannel to send the segment
                self.sendChannel.send(segmentSend)
                packet_sent += 1

        if packet_sent > 0:
            self.num_packets_sent += 3


    # ################################################################################################################ #
    # processReceive()                                                                                                 #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Manages Segment receive tasks                                                                                    #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def processReceiveAndSendRespond(self):
        # This call returns a list of incoming segments (see Segment class)...
        def sortKey(seg):
            return seg.seqnum

        listIncomingSegments = self.receiveChannel.receive()
        listIncomingSegments.sort(key=sortKey)
        prev_seq = -1
        for i in listIncomingSegments:
            if len(self.receivedDataList) > 0:
                prev_seq = max(self.receivedDataList, key=sortKey).seqnum
                # ############################################################################################################ #
                # What segments have been received?
                # How will you get them back in order?
                # This is where a majority of your logic will be implemented
            if i.seqnum - 1 == prev_seq:
                self.receivedDataList.append(i)
                self.receivedDataList.sort(key=sortKey)

                # ############################################################################################################ #
                # How do you respond to what you have received?
                # How can you tell data segments apart from ack segemnts?
                if i.seqnum >= 0:

                    # Somewhere in here you will be setting the contents of the ack segments to send.
                    # The goal is to employ cumulative ack, just like TCP does...
                    segmentAck = Segment()  # Segment acknowledging packet(s) received
                    segmentAck.setAck(i.seqnum)
                    # ############################################################################################################ #
                    # Display response segment
                    print("Sending ack: ", segmentAck.to_string())

                    # Use the unreliable sendChannel to send the ack packet
                    self.sendChannel.send(segmentAck)

            if i.seqnum < 0:
                #print("ack received: ", i.to_string())
                self.receivedAckList.append(i.acknum)
                self.receivedAckList.sort()
