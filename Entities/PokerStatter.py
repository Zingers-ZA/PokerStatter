from Entities.Suits import Suits
from Entities.Card import Card
from Entities.Player import Player
from Entities.HandEnum import handEnum
from Entities.Hand import Hand
import pprint

class PokerStatter():

    #region Properties 
    
    visibleCards = []
    allCardsDict = {}
    remainCardsDict = {}
    audienceCards = []
    currentHighestHand = Hand("default")
    currentHighestHandHolder = -1

    #endregion
    

    #   Return the chance of each player winning the current hand
    #   Expects:    allCardsDict - dictionary with seperate keys for the contained list of Card Objects
    #               players - list of player objects
    #   Returns:    Dictionary of player Id's and their percent chance of winning
    def genChancePerPlayer(self, allCardsDict, players):

        chancesPerPlayer = {}
        audienceCards = []
        totalChance = 0
        playerChance = 0

        for key in allCardsDict:
            if key == "leftOverCards":
                continue
            audienceCards = audienceCards + allCardsDict[key]
        
        self.allCardsDict = allCardsDict
        self.remainCardsDict = self.retrieveRemainingCards(audienceCards)
        self.occurencesPerCard = self.getOccurencesPerCard(audienceCards)
        self.audienceCards = audienceCards

        self.getPossibleWinningHands(players)

        for p in players:

            if p.Id != self.currentHighestHandHolder:

                for h in p.possibleWinningHands:
                    playerChance += h.chance
                    totalChance += h.chance

                chancesPerPlayer[p.Id] = playerChance * 100
        
        chancesPerPlayer[self.currentHighestHandHolder] = 100 - (totalChance * 100)
                
        return chancesPerPlayer

    #region Generic hand management 


    #   Populates each player object with a filtered list of winning Hand Objects
    #   Expects:    players - list of player Objects
    #   Returns:    null(assigns by reference to player)
    def getPossibleWinningHands(self, players):

        for p in players:
            p.possibleHands = self.getAllPossibleHands(p)

        self.currentHighestHand = self.getHighestCurrentHand(players)

        for p in players: 

            handsToCheck = []

            for key in p.possibleHands:

                if handEnum[key].value >= handEnum[self.currentHighestHand.name].value:

                    for hand in p.possibleHands[key]: #all hands(possible or not) better than the currentHighestHand
                        if hand.chance != 0 and self.compareHands(hand, self.currentHighestHand) == 1:
                            handsToCheck.append(hand)
            
            p.possibleWinningHands = handsToCheck


    #   Generates a dictionary of hands
    #   Expects:    player - the player object to use
    #   Returns:    dictionary with hand names as keys, 
    #               and lists of Hand Objects as values
    def getAllPossibleHands(self, player):

        chancesPerHand = {
            "onePair"   : self.getPossibleOnePairs(player)
        #   "twoPair"   : self.chanceOfTwoPair
        #   "trips"     : self.chanceOfTrips
        #   "straight"  : self.chanceOfStraight
        #   "flush"     : self.chanceOfFlush()
        #   "fullhouse" : self.chanceOfFullHouse
        #   "quads"     : self.chanceOfQuads
        #   "straightFlush" : self.chanceOfStraightFlush
        }

        return chancesPerHand

    #endregion
    
    #region Specific chance of hand calculation methods 

    def getPossibleOnePairs(self, player):

        possibleOnePairs = []

        allCards = []

        for key in self.allCardsDict:
            allCards += self.allCardsDict[key]
        
        visibleCards = player.cards + self.allCardsDict["TableCards"]
        
        for pCard in visibleCards :
            for c in allCards:
                if pCard.value == c.value and pCard.suit != c.suit:
                    possibleOnePairs.append(
                        Hand(
                            name    = "onePair",
                            cards   = [pCard,c],
                            chance  = self.chanceOfCard(player, c.suit, c.value)
                        ))
                        
        return possibleOnePairs
    
    def getPossibleTwoPairs(self,player):
        pass

    #endregion

    #region Comparisons and Highs 

    #   Return the highest hand out of all of the players
    #   Expects: players - list of player objects
    #   Returns: A Hand object containing the cards and name of the highest current hand
    def getHighestCurrentHand(self, players):

        highestHand = Hand("default")

        for p in players:
            for key in p.possibleHands:
                for h in p.possibleHands[key]:
                    if h.chance == 1:

                        testHand = Hand(h.name, h.cards)

                        if self.compareHands(testHand, highestHand) == 1:
                            highestHand = testHand
                            self.currentHighestHandHolder = p.Id
        
        return highestHand


    #   Determines which hand from 2 given hands will win
    #   Expects: hand1 - first compare Hand Object 
    #            hand2 - second compare Hand Object
    #   Returns: Numeric representation of which hand won (1 or 2, or 0 if draw)
    def compareHands(self,hand1,hand2):

        if handEnum[hand1.name].value > handEnum[hand2.name].value:
            return 1
        elif handEnum[hand1.name].value < handEnum[hand2.name].value:
            return 2
        else:
            # same combo, find higher kicker(s)

            # possible here to just find the highest card in the cards lists? 
            # ie. one pair, if the highest card from p1.cards + p2.cards gives you the winner
            # two pair? 
            # trips?
            # straight?
            
            if hand1.name == "onePair":

                return self.highest(hand1.cards[0].value, hand2.cards[0].value)

            elif hand1.name == "twoPair":
                pass
            elif hand1.name == "trips":
                pass
            elif hand1.name == "straight":
                pass
            elif hand1.name == "flush":
                pass
            elif hand1.name == "fullHouse":
                pass
            elif hand1.name == "quads":
                pass
            elif hand1.name == "straightflush":
                pass

    def highest(self, value1, value2):
        if value1 > value2:
            return 1
        elif value1 < value2:
            return 2
        else:
            return 0

    def beatsHands(self,hand1,hands):
        pass

    #endregion

    #region Card utilities 

    #   Retrieve the percent chance of getting a card with matching parameters
    #   Expects:    player  - the current player object being worked on 
    #               suit    - optional suit enum to match on
    #               value   - optional numeric card value to match on
    #   Returns:    the percent chance of getting a card that matches the supplied criteria
    def chanceOfCard(self, player, suit = None, value = None):
        
        remainingCardsCount = float(52 - len(self.audienceCards))

        otherPlayerCards = []

        for key in self.allCardsDict:
            if key != "TableCards" and key != "leftOverCards" and key != player.Id:
                otherPlayerCards += self.allCardsDict[key]
        
        if suit != None and value != None:
            for c in self.allCardsDict[player.Id]:
                if c.value == value and c.suit == suit:
                    return 1
            for c in self.allCardsDict["TableCards"]:
                if c.value == value and c.suit == suit:
                    return 1
            for c in otherPlayerCards:
                if c.value == value and c.suit == suit:
                    return 0
            return 1/remainingCardsCount
        elif suit == None and value != None:
            return self.remainCardsDict[value]/remainingCardsCount
        elif suit != None and value == None:
            return  self.remainCardsDict[suit.name[0]]/remainingCardsCount
        else:
            return "u knob"

    
    #   Remove the given cardSet from a set of cards and return counts of the rest of the cards
    #   Expects: cardSet - list of Card Objects to exclude
    #   Returns: dictionary where each card value and suit is a key, and values are the amount
    #            of the specific key are left in the deck
    def retrieveRemainingCards(self, cardSet):

        occurencesPerCard = self.getOccurencesPerCard(cardSet)
        remaining = {}
        suits = ["C","H","S","D"]

        for i in range(13):
            if (i+1) in occurencesPerCard:
                remaining[i+1] = 4 - occurencesPerCard[i+1]
            else:
                remaining[i+1] = 4

        for s in suits:
            if s in occurencesPerCard:
                remaining[s] = 13 - occurencesPerCard[s]
            else:
                remaining[s] = 13

        return remaining


    #   Create totals for how many of each card value and suit exist inside a given cardSet
    #   Expects:    cardSet - list of Card objects to tally up
    #   Returns:    dictionary where each card value and suit is a key, and values are the amount
    #               of the specific key exist in the card set
    def getOccurencesPerCard(self, cardSet):
        tempDict = {
            "C": 0,
            "D": 0,
            "S": 0,
            "H": 0
        }

        for c in cardSet:
            suit = c.getSuitShort()
               
            if c.value in tempDict:
                tempDict[c.value] = tempDict[c.value] + 1 
            else:
                tempDict[c.value] = 1

            if suit in tempDict:
                tempDict[suit] = tempDict[suit] + 1
            else:
                 tempDict[suit] = 1

        return tempDict

    #endregion
