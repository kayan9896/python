public class KnockoutTournament {
    private final Match[] roundOf16;
    private final Match[] quarterFinals;
    private final Match[] semiFinals;
    private final Match finalMatch;

    public KnockoutTournament(Team[] teams) {
        roundOf16 = initializeRound(teams, 16);
        quarterFinals = initializeRound(null, 8);
        semiFinals = initializeRound(null, 4);
        finalMatch = new Match(null, null);

        linkMatches(roundOf16, quarterFinals);
        linkMatches(quarterFinals, semiFinals);
        linkMatches(semiFinals, new Match[]{finalMatch});
    }

    private Match[] initializeRound(Team[] teams, int size) {
        Match[] round = new Match[size / 2];
        for (int i = 0; i < size / 2; i++) {
            if (teams == null) {
                round[i] = new Match(null, null);
            } else {
                round[i] = new Match(teams[i * 2], teams[i * 2 + 1]);
            }
        }
        return round;
    }

    private void linkMatches(Match[] currentRound, Match[] nextRound) {
        for (int i = 0; i < currentRound.length; i++) {
            currentRound[i].setNextMatch(nextRound[i / 2]);
        }
    }

    public void simulateTournament() {
        simulateRound(roundOf16);
        simulateRound(quarterFinals);
        simulateRound(semiFinals);
        finalMatch.simulateMatch();
        Team winner = finalMatch.getWinner();
        System.out.println("The winner of the tournament is: " + winner.name);
    }

    private void simulateRound(Match[] round) {
        for (int i = 0; i < round.length; i++) {
            round[i].simulateMatch();
            if (i % 2 == 0) {
                round[i].nextMatch.homeTeam = round[i].getWinner();
            } else {
                round[i].nextMatch.awayTeam = round[i].getWinner();
            }
        }
    }

    public void printBracket(Match[] round, int level) {
        if (round == null) {
            return;
        }

        for (Match match : round) {
            for (int i = 0; i < level; i++) {
                System.out.print("  ");
            }

            System.out.println(match.homeTeam.name + " vs " + match.awayTeam.name);
            System.out.println("Winner: " + match.getWinner().name);
        }

        if (round.length > 1) {
            Match[] nextRound = new Match[round.length / 2];
            for (int i = 0; i < round.length; i++) {
                nextRound[i / 2] = round[i].nextMatch;
            }
            printBracket(nextRound, level + 1);
        }
    }

    public void printTournamentBracket() {
        printBracket(roundOf16, 0);
    }
}

public class Match {
    public Team homeTeam;
    public Team awayTeam;
    public Match nextMatch;
    public Team winnerTeam;

    public Match(Team homeTeam, Team awayTeam) {
        this.homeTeam = homeTeam;
        this.awayTeam = awayTeam;
    }

    public void setNextMatch(Match nextMatch) {
        this.nextMatch = nextMatch;
    }

    public Team getWinner() {
        return this.winnerTeam;
    }

    public Team playMatch() {
        return this.getWinner();
    }

    public int[] simulateMatch() {
        int homeGoals = (int) (Math.random() * 5);
        int awayGoals = (int) (Math.random() * 5);
        if (homeGoals > awayGoals) {
            this.winnerTeam = homeTeam;
        } else if (awayGoals > homeGoals) {
            this.winnerTeam = awayTeam;
        } else {
            // Handle the case where the teams draw
            // For example, you could simulate a penalty shootout
            if (Math.random() < 0.5) {
                this.winnerTeam = homeTeam;
            } else {
                this.winnerTeam = awayTeam;
            }
        }
        return new int[]{homeGoals, awayGoals};
    }
}

public class Team {
    public String name;
    public String league;
    public int wins;
    public int losses;
    public int draws;
    public int points;
    public int goalsFor;
    public int goalsAgainst;

    public Team(String name, String league) {
        this.name = name;
        this.league = league;
        this.wins = 0;
        this.losses = 0;
        this.draws = 0;
        this.points = 0;
        this.goalsFor = 0;
        this.goalsAgainst = 0;
    }
}
