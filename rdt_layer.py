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
    num_packets_sent = 0
    receivedDataList = []
    cumulative_ack = 0
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

        self.num_packets_sent = 0
        self.receivedDataList = []
        self.cumulative_ack = 0
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
        data = ""

        for i in self.receivedDataList:
            data += i.payload

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

        packet_sent = 0
        max_packets = int(self.FLOW_CONTROL_WIN_SIZE / self.DATA_LENGTH)
        window_start = self.cumulative_ack

        # Send packets in Window
        while packet_sent < max_packets and len(self.dataToSend) > 0:
            seg_start = window_start * self.DATA_LENGTH
            seg_end = (window_start + 1) * self.DATA_LENGTH

            data = self.dataToSend[seg_start:seg_end]

            # Send segment if there is data left to send
            if data:
                # Create segment to send
                segmentSend = Segment()
                segmentSend.setData(window_start, data)

                # Display sending segment
                print("Sending segment: ", segmentSend.to_string())

                # Use the unreliable sendChannel to send the segment
                self.sendChannel.send(segmentSend)

            packet_sent += 1
            window_start += 1

    # ################################################################################################################ #
    # processReceive()                                                                                                 #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Manages Segment receive tasks                                                                                    #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def processReceiveAndSendRespond(self):

        # Key to sort a list of segments by sequence number
        def sortKey(seg):
            return seg.seqnum

        # This call returns a list of incoming segments (see Segment class)...
        listIncomingSegments = self.receiveChannel.receive()

        # Sort the incoming segments by segment number
        listIncomingSegments.sort(key=sortKey)

        # Iterate through incoming segments
        for i in listIncomingSegments:
            segmentAck = Segment()  # Segment acknowledging packet(s) received

            # Server receiving packet from client
            if i.seqnum >= 0:

                # Add valid packet to output list and set ack
                if i.seqnum == self.cumulative_ack and i.checkChecksum() is True:
                    segmentAck.setAck(i.seqnum + 1)
                    self.cumulative_ack += 1
                    self.receivedDataList.append(i)
                    self.receivedDataList.sort(key=sortKey)

                # Invalid packet reset ack
                else:
                    segmentAck.setAck(self.cumulative_ack)

                # Display response segment
                print("Sending ack: ", segmentAck.to_string())

                # Use the unreliable sendChannel to send the ack packet
                self.sendChannel.send(segmentAck)

            # Client receives ack from Server
            elif i.seqnum < 0:

                # Add new ack to cumulative total
                if i.acknum > self.cumulative_ack - 1:
                    self.cumulative_ack = i.acknum
                    print("ack received: ", i.to_string())

